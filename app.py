def compare_tool_calls(expected_tool_calls, actual_tool_calls):
    from copy import deepcopy

    result = {"comparison_result": {"tools": [], "overall_summary": {}}}

    # Group tools by name to handle multiple calls
    expected_tools_grouped = {}
    for t in expected_tool_calls:
        expected_tools_grouped.setdefault(t["tool_name"], []).append(t)

    actual_tools_grouped = {}
    for t in actual_tool_calls:
        actual_tools_grouped.setdefault(t["name"], []).append(t)

    expected_tool_names = set(expected_tools_grouped.keys())
    actual_tool_names = set(actual_tools_grouped.keys())

    matched_tool_count = len(expected_tool_names & actual_tool_names)
    unexpected_tools = actual_tool_names - expected_tool_names

    tools_summary = []
    tool_call_accuracies = []
    intent_accuracies = []
    field_accuracies = []

    # Loop through all expected tools
    for tool_name, expected_tool_list in expected_tools_grouped.items():
        actual_tool_list = actual_tools_grouped.get(tool_name, [])

        # Compare each expected occurrence
        for idx, expected_tool in enumerate(expected_tool_list):
            # Take corresponding actual tool if exists, else empty
            actual_tool = actual_tool_list[idx] if idx < len(actual_tool_list) else None

            tool_summary = {
                "tool_name": tool_name,
                "tool_call_accuracy": 1.0 if actual_tool else 0.0,
                "unexpected_tool_call": bool(unexpected_tools & {tool_name}),
                "extra_intents": [],
                "missing_intents": [],
                "unexpected_intent": False,
                "intent_summary": [],
                "intent_accuracy": 1.0,
                "average_field_accuracy": 1.0,
                "passed": True
            }

            if not actual_tool:
                # Tool missing entirely
                tool_summary["intent_accuracy"] = 0.0
                tool_summary["average_field_accuracy"] = 0.0
                tool_summary["passed"] = False
                tools_summary.append(tool_summary)
                tool_call_accuracies.append(0.0)
                intent_accuracies.append(0.0)
                field_accuracies.append(0.0)
                continue

            intents = ["add", "update", "delete"]
            intent_acc_list = []
            field_acc_list = []

            # Detect missing/extra intents
            expected_intents_present = [i for i in intents if expected_tool.get("expected_input", {}).get(i)]
            actual_intents_present = [i for i in intents if actual_tool.get("input", {}).get(i)]

            missing_intents = [i for i in expected_intents_present if i not in actual_intents_present]
            extra_intents = [i for i in actual_intents_present if i not in expected_intents_present]

            tool_summary["missing_intents"] = missing_intents
            tool_summary["extra_intents"] = extra_intents
            tool_summary["unexpected_intent"] = True if extra_intents else False

            if tool_summary["unexpected_intent"]:
                tool_summary["passed"] = False

            # Compare fields per intent
            for intent in intents:
                expected_records = expected_tool.get("expected_input", {}).get(intent, [])
                actual_records = actual_tool.get("input", {}).get(intent, [])

                intent_records_summary = []
                max_len = max(len(expected_records), len(actual_records))

                for ridx in range(max_len):
                    expected_record = expected_records[ridx] if ridx < len(expected_records) else {}
                    actual_record = actual_records[ridx] if ridx < len(actual_records) else {}
                    field_comparisons = {}
                    correct_fields = 0
                    total_fields = len(expected_record)

                    # Compare only expected fields
                    for field, expected_value in expected_record.items():
                        actual_value = actual_record.get(field)
                        correct = expected_value == actual_value
                        if correct:
                            correct_fields += 1
                        field_comparisons[field] = {
                            "expected": expected_value,
                            "actual": actual_value,
                            "correct": correct
                        }

                    record_field_accuracy = correct_fields / total_fields if total_fields > 0 else 1.0

                    unexpected_record = False
                    if ridx >= len(expected_records) and actual_record:
                        # Extra record in actual
                        unexpected_record = True
                        record_field_accuracy = 0.0

                    intent_records_summary.append({
                        "record_index": ridx,
                        "field_comparisons": field_comparisons,
                        "present_fields_correct": correct_fields,
                        "present_fields_total": total_fields,
                        "present_fields_accuracy": record_field_accuracy,
                        "unexpected_record": unexpected_record
                    })

                    field_acc_list.append(record_field_accuracy)

                # Intent accuracy: consider only expected intents
                if expected_records:
                    intent_acc = 1.0 if len(expected_records) == len(actual_records[:len(expected_records)]) else 0.0
                else:
                    intent_acc = 1.0

                intent_acc_list.append(intent_acc)

                if expected_records:
                    tool_summary["intent_summary"].append({
                        "intent": intent,
                        "records": intent_records_summary
                    })

            # Tool-level metrics
            tool_summary["intent_accuracy"] = min(intent_acc_list) if intent_acc_list else 1.0
            tool_summary["average_field_accuracy"] = sum(field_acc_list)/len(field_acc_list) if field_acc_list else 1.0

            # Strict tool-level pass/fail
            tool_summary["passed"] = (
                tool_summary["tool_call_accuracy"] == 1.0 and
                tool_summary["intent_accuracy"] == 1.0 and
                tool_summary["average_field_accuracy"] == 1.0 and
                not tool_summary["extra_intents"] and
                not tool_summary["missing_intents"] and
                not tool_summary["unexpected_tool_call"] and
                not tool_summary["unexpected_intent"]
            )

            tools_summary.append(tool_summary)
            tool_call_accuracies.append(tool_summary["tool_call_accuracy"])
            intent_accuracies.append(tool_summary["intent_accuracy"])
            field_accuracies.append(tool_summary["average_field_accuracy"])

    # Overall summary
    overall_summary = {
        "expected_tool_count": len(expected_tool_calls),
        "actual_tool_count": len(actual_tool_calls),
        "matched_tool_count": matched_tool_count,
        "tool_call_accuracy": sum(tool_call_accuracies)/len(tool_call_accuracies) if tool_call_accuracies else 0.0,
        "average_intent_accuracy": sum(intent_accuracies)/len(intent_accuracies) if intent_accuracies else 0.0,
        "average_field_accuracy": sum(field_accuracies)/len(field_accuracies) if field_accuracies else 0.0,
        "final_accuracy": (
            sum(tool_call_accuracies)/len(tool_call_accuracies) +
            sum(intent_accuracies)/len(intent_accuracies) +
            sum(field_accuracies)/len(field_accuracies)
        ) / 3 if tool_call_accuracies else 0.0,
        "passed": all([t["passed"] for t in tools_summary])
    }

    result["comparison_result"]["tools"] = tools_summary
    result["comparison_result"]["overall_summary"] = overall_summary

    return result
