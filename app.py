def compare_tool_calls(expected_tool_calls, actual_tool_calls):
    from copy import deepcopy

    result = {"comparison_result": {"tools": [], "overall_summary": {}}}

    # Convert to dict for easy access
    expected_tools_dict = {t["tool_name"]: t for t in expected_tool_calls}
    actual_tools_dict = {t["name"]: t for t in actual_tool_calls}

    expected_tool_names = set(expected_tools_dict.keys())
    actual_tool_names = set(actual_tools_dict.keys())

    matched_tool_count = len(expected_tool_names & actual_tool_names)
    unexpected_tools = actual_tool_names - expected_tool_names

    tools_summary = []
    tool_call_accuracies = []
    intent_accuracies = []
    field_accuracies = []

    for tool_name, expected_tool in expected_tools_dict.items():
        tool_summary = {
            "tool_name": tool_name,
            "tool_call_accuracy": 1.0 if tool_name in actual_tools_dict else 0.0,
            "unexpected_tool_call": bool(unexpected_tools & {tool_name}),
            "extra_intents": [],
            "missing_intents": [],
            "unexpected_intent": False,
            "intent_summary": [],
            "intent_accuracy": 1.0,
            "average_field_accuracy": 1.0,
            "passed": True
        }

        if tool_name not in actual_tools_dict:
            # Tool missing entirely
            tool_summary["intent_accuracy"] = 0.0
            tool_summary["average_field_accuracy"] = 0.0
            tool_summary["passed"] = False
            tools_summary.append(tool_summary)
            tool_call_accuracies.append(0.0)
            intent_accuracies.append(0.0)
            field_accuracies.append(0.0)
            continue

        actual_tool = actual_tools_dict[tool_name]
        intents = ["add", "update", "delete"]

        intent_acc_list = []
        field_acc_list = []

        # Detect missing/extra intents
        expected_intents_present = [i for i in intents if expected_tool.get("input", {}).get(i)]
        actual_intents_present = [i for i in intents if actual_tool.get("input", {}).get(i)]

        missing_intents = [i for i in expected_intents_present if i not in actual_intents_present]
        extra_intents = [i for i in actual_intents_present if i not in expected_intents_present]

        tool_summary["missing_intents"] = missing_intents
        tool_summary["extra_intents"] = extra_intents
        tool_summary["unexpected_intent"] = True if extra_intents else False

        if tool_summary["unexpected_intent"]:
            tool_summary["passed"] = False  # fail if unexpected intent exists

        # Compare fields per intent
        for intent in intents:
            expected_records = expected_tool.get("input", {}).get(intent, [])
            actual_records = actual_tool.get("input", {}).get(intent, [])

            intent_records_summary = []
            max_len = max(len(expected_records), len(actual_records))

            for idx in range(max_len):
                expected_record = expected_records[idx] if idx < len(expected_records) else {}
                actual_record = actual_records[idx] if idx < len(actual_records) else {}
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
                if idx >= len(expected_records) and actual_record:
                    # Extra record in actual
                    unexpected_record = True
                    record_field_accuracy = 0.0

                intent_records_summary.append({
                    "record_index": idx,
                    "field_comparisons": field_comparisons,
                    "present_fields_correct": correct_fields,
                    "present_fields_total": total_fields,
                    "present_fields_accuracy": record_field_accuracy,
                    "unexpected_record": unexpected_record
                })

                field_acc_list.append(record_field_accuracy)

            # Intent accuracy: consider only expected intents, ignore extra actual intents
            if expected_records:
                intent_acc = 1.0 if (len(expected_records) == len(actual_records[:len(expected_records)])) else 0.0
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
