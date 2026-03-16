import ast
import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from functools import wraps

from flask import Response, Flask, jsonify, redirect, render_template_string, request, session, url_for

from css import css_content
from html import DASHBOARD_TEMPLATE, WORKFLOW_DETAIL_TEMPLATE


app = Flask(__name__)
app.secret_key = "halleyx-workflow-engine-demo-secret"

DB_FILE = "database.json"
DEFAULT_MAX_ITERATIONS = 15
STEP_TYPES = {"task", "approval", "notification"}


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_id():
    return str(uuid.uuid4())


def base_db():
    return {
        "workflows": [],
        "steps": [],
        "rules": [],
        "executions": [],
        "users": [],
    }


def init_db():
    needs_seed = False
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        needs_seed = True
    else:
        try:
            with open(DB_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            needs_seed = not isinstance(data, dict)
        except (json.JSONDecodeError, OSError):
            needs_seed = True

    if needs_seed:
        data = base_db()
        seed_sample_workflow(data)
        save_db(data)


def load_db():
    init_db()
    with open(DB_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if ensure_db_defaults(data):
        save_db(data)
    return data


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def default_users():
    return [
        {
            "id": new_id(),
            "name": "Maya Manager",
            "username": "manager",
            "password": "manager123",
            "email": "manager@example.com",
            "role": "manager",
            "created_at": now_iso(),
        },
        {
            "id": new_id(),
            "name": "Felix Finance",
            "username": "finance",
            "password": "finance123",
            "email": "finance@example.com",
            "role": "finance",
            "created_at": now_iso(),
        },
        {
            "id": new_id(),
            "name": "Cora Chief Executive",
            "username": "ceo",
            "password": "ceo123",
            "email": "ceo@example.com",
            "role": "ceo",
            "created_at": now_iso(),
        },
        {
            "id": new_id(),
            "name": "Riya Requester",
            "username": "requester",
            "password": "requester123",
            "email": "requester@example.com",
            "role": "employee",
            "created_at": now_iso(),
        },
    ]


def ensure_db_defaults(db):
    changed = False
    for key in base_db():
        if key not in db:
            db[key] = [] if key != "users" else []
            changed = True

    if not db["users"]:
        db["users"] = default_users()
        changed = True
    return changed


def seed_sample_workflow(db):
    workflow_id = new_id()
    workflow_key = workflow_id
    created_at = now_iso()
    workflow = {
        "id": workflow_id,
        "workflow_key": workflow_key,
        "name": "Expense Approval",
        "description": "Sample workflow with branching approvals and notifications.",
        "version": 1,
        "is_active": True,
        "input_schema": {
            "amount": {"type": "number", "required": True},
            "country": {"type": "string", "required": True},
            "department": {"type": "string", "required": False},
            "priority": {
                "type": "string",
                "required": True,
                "allowed_values": ["High", "Medium", "Low"],
            },
        },
        "start_step_id": "",
        "max_iterations": DEFAULT_MAX_ITERATIONS,
        "created_at": created_at,
        "updated_at": created_at,
    }

    step_ids = {
        "manager": new_id(),
        "finance": new_id(),
        "ceo": new_id(),
        "rejection": new_id(),
    }

    steps = [
        {
            "id": step_ids["manager"],
            "workflow_id": workflow_id,
            "name": "Manager Approval",
            "step_type": "approval",
            "order": 1,
            "metadata": {"assignee_email": "manager@example.com"},
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "id": step_ids["finance"],
            "workflow_id": workflow_id,
            "name": "Finance Notification",
            "step_type": "notification",
            "order": 2,
            "metadata": {"notification_channel": "email", "template": "finance-review"},
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "id": step_ids["ceo"],
            "workflow_id": workflow_id,
            "name": "CEO Approval",
            "step_type": "approval",
            "order": 3,
            "metadata": {"assignee_email": "ceo@example.com"},
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "id": step_ids["rejection"],
            "workflow_id": workflow_id,
            "name": "Task Rejection",
            "step_type": "task",
            "order": 4,
            "metadata": {"instructions": "Mark request rejected and notify requester."},
            "created_at": created_at,
            "updated_at": created_at,
        },
    ]

    rules = [
        {
            "id": new_id(),
            "step_id": step_ids["manager"],
            "condition": "amount > 100 && country == 'US' && priority == 'High'",
            "next_step_id": step_ids["finance"],
            "priority": 1,
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "id": new_id(),
            "step_id": step_ids["manager"],
            "condition": "amount <= 100 || department == 'HR'",
            "next_step_id": step_ids["ceo"],
            "priority": 2,
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "id": new_id(),
            "step_id": step_ids["manager"],
            "condition": "priority == 'Low' && country != 'US'",
            "next_step_id": step_ids["rejection"],
            "priority": 3,
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "id": new_id(),
            "step_id": step_ids["manager"],
            "condition": "DEFAULT",
            "next_step_id": step_ids["rejection"],
            "priority": 4,
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "id": new_id(),
            "step_id": step_ids["finance"],
            "condition": "DEFAULT",
            "next_step_id": step_ids["ceo"],
            "priority": 1,
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "id": new_id(),
            "step_id": step_ids["ceo"],
            "condition": "DEFAULT",
            "next_step_id": None,
            "priority": 1,
            "created_at": created_at,
            "updated_at": created_at,
        },
        {
            "id": new_id(),
            "step_id": step_ids["rejection"],
            "condition": "DEFAULT",
            "next_step_id": None,
            "priority": 1,
            "created_at": created_at,
            "updated_at": created_at,
        },
    ]

    workflow["start_step_id"] = step_ids["manager"]
    db["workflows"].append(workflow)
    db["steps"].extend(steps)
    db["rules"].extend(rules)


def json_error(message, status=400):
    return jsonify({"error": message}), status


def get_json_payload():
    payload = request.get_json(silent=True)
    if isinstance(payload, dict):
        return payload
    return {}


def find_workflow(db, workflow_id):
    return next((workflow for workflow in db["workflows"] if workflow["id"] == workflow_id), None)


def find_step(db, step_id):
    return next((step for step in db["steps"] if step["id"] == step_id), None)


def find_rule(db, rule_id):
    return next((rule for rule in db["rules"] if rule["id"] == rule_id), None)


def find_execution(db, execution_id):
    return next((execution for execution in db["executions"] if execution["id"] == execution_id), None)


def find_user_by_id(db, user_id):
    return next((user for user in db["users"] if user["id"] == user_id), None)


def find_user_by_username(db, username):
    return next((user for user in db["users"] if user["username"] == username), None)


def find_user_by_email(db, email):
    return next((user for user in db["users"] if user["email"].lower() == str(email).lower()), None)


def get_steps_for_workflow(db, workflow_id):
    return sorted(
        [step for step in db["steps"] if step["workflow_id"] == workflow_id],
        key=lambda step: (step.get("order", 0), step["name"]),
    )


def get_rules_for_step(db, step_id):
    return sorted(
        [rule for rule in db["rules"] if rule["step_id"] == step_id],
        key=lambda rule: (rule.get("priority", 999999), rule["created_at"]),
    )


def get_workflow_bundle(db, workflow_id):
    workflow = find_workflow(db, workflow_id)
    if not workflow:
        return None

    steps = get_steps_for_workflow(db, workflow_id)
    rules_by_step = {step["id"]: get_rules_for_step(db, step["id"]) for step in steps}
    return {
        "workflow": workflow,
        "steps": steps,
        "rules_by_step": rules_by_step,
    }


def list_latest_workflows(db, search="", page=1, per_page=10):
    latest = {}
    for workflow in db["workflows"]:
        key = workflow["workflow_key"]
        current = latest.get(key)
        if not current or workflow["version"] > current["version"]:
            latest[key] = workflow

    items = list(latest.values())
    if search:
        search_lower = search.lower()
        items = [
            workflow
            for workflow in items
            if search_lower in workflow["name"].lower() or search_lower in workflow["id"].lower()
        ]

    items.sort(key=lambda workflow: workflow["updated_at"], reverse=True)
    total = len(items)
    start = max(page - 1, 0) * per_page
    end = start + per_page
    return items[start:end], total


def parse_metadata(value):
    if isinstance(value, dict):
        return value
    if value in (None, ""):
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def parse_schema(value):
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    return json.loads(value)


def normalize_schema(schema):
    control_keys = {"type", "required", "allowed_values"}
    normalized = {}
    for field, config in schema.items():
        if not isinstance(config, dict):
            config = {
                "type": infer_type_from_example(config),
                "required": True,
                "allowed_values": [],
            }
        elif "type" not in config:
            example_value = next(
                (value for key, value in config.items() if key not in control_keys),
                None,
            )
            if example_value is None:
                raise ValueError(f"Schema for '{field}' must define a type or example value.")
            config = {
                "type": infer_type_from_example(example_value),
                "required": bool(config.get("required", False)),
                "allowed_values": config.get("allowed_values") or [],
            }

        field_type = config.get("type")
        if field_type not in {"string", "number", "boolean"}:
            raise ValueError(f"Unsupported type for '{field}'.")
        allowed_values = config.get("allowed_values") or []
        normalized[field] = {
            "type": field_type,
            "required": bool(config.get("required", False)),
            "allowed_values": allowed_values,
        }
    return normalized


def infer_type_from_example(value):
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    return "string"


def validate_input_schema(schema, payload):
    errors = []
    for field, config in schema.items():
        required = config.get("required", False)
        field_type = config.get("type")
        allowed_values = config.get("allowed_values") or []
        value = payload.get(field)

        if required and value in (None, ""):
            errors.append(f"'{field}' is required.")
            continue
        if value in (None, ""):
            continue

        if field_type == "number" and not isinstance(value, (int, float)):
            errors.append(f"'{field}' must be a number.")
        if field_type == "string" and not isinstance(value, str):
            errors.append(f"'{field}' must be a string.")
        if field_type == "boolean" and not isinstance(value, bool):
            errors.append(f"'{field}' must be a boolean.")
        if allowed_values and value not in allowed_values:
            errors.append(f"'{field}' must be one of {allowed_values}.")
    return errors


def parse_form_value(raw_value, field_type):
    if raw_value == "":
        return None
    if field_type == "number":
        return float(raw_value) if "." in raw_value else int(raw_value)
    if field_type == "boolean":
        return raw_value.lower() in {"true", "1", "yes", "on"}
    return raw_value


def form_payload_from_schema(schema, form_data):
    payload = {}
    for field, config in schema.items():
        payload[field] = parse_form_value(form_data.get(field, ""), config["type"])
    return payload


def clone_workflow_version(db, workflow_id, updates):
    existing = find_workflow(db, workflow_id)
    if not existing:
        raise ValueError("Workflow not found.")

    family_id = existing["workflow_key"]
    family_versions = [workflow for workflow in db["workflows"] if workflow["workflow_key"] == family_id]
    next_version = max(workflow["version"] for workflow in family_versions) + 1

    for workflow in family_versions:
        workflow["is_active"] = False
        workflow["updated_at"] = now_iso()

    new_workflow_id = new_id()
    created_at = now_iso()
    new_workflow = deepcopy(existing)
    new_workflow.update(updates)
    new_workflow["id"] = new_workflow_id
    new_workflow["workflow_key"] = family_id
    new_workflow["version"] = next_version
    new_workflow["is_active"] = True
    new_workflow["created_at"] = created_at
    new_workflow["updated_at"] = created_at
    new_workflow["start_step_id"] = ""

    old_steps = get_steps_for_workflow(db, workflow_id)
    id_map = {}
    cloned_steps = []
    cloned_rules = []
    for step in old_steps:
        new_step_id = new_id()
        id_map[step["id"]] = new_step_id
        cloned_step = deepcopy(step)
        cloned_step["id"] = new_step_id
        cloned_step["workflow_id"] = new_workflow_id
        cloned_step["created_at"] = created_at
        cloned_step["updated_at"] = created_at
        cloned_steps.append(cloned_step)

    for step in old_steps:
        for rule in get_rules_for_step(db, step["id"]):
            cloned_rule = deepcopy(rule)
            cloned_rule["id"] = new_id()
            cloned_rule["step_id"] = id_map[rule["step_id"]]
            cloned_rule["next_step_id"] = id_map.get(rule["next_step_id"])
            cloned_rule["created_at"] = created_at
            cloned_rule["updated_at"] = created_at
            cloned_rules.append(cloned_rule)

    new_workflow["start_step_id"] = id_map.get(existing.get("start_step_id"), "")
    db["workflows"].append(new_workflow)
    db["steps"].extend(cloned_steps)
    db["rules"].extend(cloned_rules)
    return new_workflow


def delete_workflow_family(db, workflow_id):
    workflow = find_workflow(db, workflow_id)
    if not workflow:
        return False

    family_id = workflow["workflow_key"]
    workflow_ids = [item["id"] for item in db["workflows"] if item["workflow_key"] == family_id]
    step_ids = [step["id"] for step in db["steps"] if step["workflow_id"] in workflow_ids]

    db["workflows"] = [item for item in db["workflows"] if item["workflow_key"] != family_id]
    db["steps"] = [step for step in db["steps"] if step["workflow_id"] not in workflow_ids]
    db["rules"] = [rule for rule in db["rules"] if rule["step_id"] not in step_ids]
    db["executions"] = [execution for execution in db["executions"] if execution["workflow_id"] not in workflow_ids]
    return True


def prepare_expression(condition):
    return (
        condition.replace("&&", " and ")
        .replace("||", " or ")
        .replace("true", "True")
        .replace("false", "False")
    )


class SafeExpressionEvaluator(ast.NodeVisitor):
    def __init__(self, context):
        self.context = context

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Name(self, node):
        if node.id in self.context:
            return self.context[node.id]
        raise ValueError(f"Unknown field '{node.id}'.")

    def visit_Constant(self, node):
        return node.value

    def visit_BoolOp(self, node):
        if isinstance(node.op, ast.And):
            return all(self.visit(value) for value in node.values)
        if isinstance(node.op, ast.Or):
            return any(self.visit(value) for value in node.values)
        raise ValueError("Unsupported logical operator.")

    def visit_Compare(self, node):
        left = self.visit(node.left)
        for operator, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            if isinstance(operator, ast.Eq):
                result = left == right
            elif isinstance(operator, ast.NotEq):
                result = left != right
            elif isinstance(operator, ast.Lt):
                result = left < right
            elif isinstance(operator, ast.LtE):
                result = left <= right
            elif isinstance(operator, ast.Gt):
                result = left > right
            elif isinstance(operator, ast.GtE):
                result = left >= right
            else:
                raise ValueError("Unsupported comparison operator.")
            if not result:
                return False
            left = right
        return True

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function call.")
        function_name = node.func.id
        args = [self.visit(argument) for argument in node.args]

        if function_name == "contains" and len(args) == 2:
            return str(args[1]) in str(args[0])
        if function_name == "startsWith" and len(args) == 2:
            return str(args[0]).startswith(str(args[1]))
        if function_name == "endsWith" and len(args) == 2:
            return str(args[0]).endswith(str(args[1]))
        raise ValueError(f"Unsupported function '{function_name}'.")

    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.Not):
            return not self.visit(node.operand)
        raise ValueError("Unsupported unary operator.")

    def generic_visit(self, node):
        raise ValueError(f"Unsupported syntax: {type(node).__name__}")


def evaluate_condition(condition, data):
    if condition == "DEFAULT":
        return True, None
    try:
        expression = ast.parse(prepare_expression(condition), mode="eval")
        evaluator = SafeExpressionEvaluator(data)
        return bool(evaluator.visit(expression)), None
    except Exception as exc:
        return False, str(exc)


def evaluate_step_rules(rules, payload):
    evaluated_rules = []
    matched_rule = None
    rule_errors = []

    for rule in rules:
        result, error = evaluate_condition(rule["condition"], payload)
        evaluated_rules.append(
            {
                "rule": rule["condition"],
                "result": result,
                "error": error,
                "priority": rule["priority"],
            }
        )
        if error:
            rule_errors.append(error)
            continue
        if result and matched_rule is None:
            matched_rule = rule
            if rule["condition"] != "DEFAULT":
                break

    status = "completed"
    error_message = None
    next_step_id = matched_rule["next_step_id"] if matched_rule else None
    if matched_rule is None:
        status = "failed"
        error_message = "No matching rule found, including DEFAULT."
    elif rule_errors and matched_rule["condition"] == "DEFAULT":
        status = "failed"
        error_message = "One or more rule conditions were invalid, DEFAULT fallback used."

    return {
        "evaluated_rules": evaluated_rules,
        "matched_rule": matched_rule,
        "status": status,
        "error_message": error_message,
        "next_step_id": next_step_id,
    }


def run_step(step, rules, payload, triggered_by):
    started_at = now_iso()
    rule_outcome = evaluate_step_rules(rules, payload)

    log_entry = {
        "step_id": step["id"],
        "step_name": step["name"],
        "step_type": step["step_type"],
        "metadata": step["metadata"],
        "evaluated_rules": rule_outcome["evaluated_rules"],
        "selected_next_step": rule_outcome["next_step_id"],
        "selected_next_step_name": None,
        "status": rule_outcome["status"],
        "approver_id": triggered_by if step["step_type"] == "approval" else None,
        "error_message": rule_outcome["error_message"],
        "started_at": started_at,
        "ended_at": now_iso(),
    }
    return log_entry, rule_outcome["next_step_id"]


def execute_workflow_internal(
    db,
    workflow,
    payload,
    triggered_by="system",
    resume_from_step_id=None,
    existing_logs=None,
    retries=0,
):
    schema_errors = validate_input_schema(workflow["input_schema"], payload)
    if schema_errors:
        raise ValueError("; ".join(schema_errors))

    steps = get_steps_for_workflow(db, workflow["id"])
    step_map = {step["id"]: step for step in steps}
    rules_map = {step["id"]: get_rules_for_step(db, step["id"]) for step in steps}

    execution_id = new_id()
    started_at = now_iso()
    current_step_id = resume_from_step_id or workflow["start_step_id"]
    logs = deepcopy(existing_logs) if existing_logs else []
    status = "in_progress"
    iterations = 0
    failed_step_id = None

    while current_step_id:
        iterations += 1
        if iterations > workflow.get("max_iterations", DEFAULT_MAX_ITERATIONS):
            status = "failed"
            failed_step_id = current_step_id
            logs.append(
                {
                    "step_id": current_step_id,
                    "step_name": step_map.get(current_step_id, {}).get("name", "Unknown"),
                    "step_type": step_map.get(current_step_id, {}).get("step_type", "task"),
                    "metadata": {},
                    "evaluated_rules": [],
                    "selected_next_step": None,
                    "selected_next_step_name": None,
                    "status": "failed",
                    "approver_id": None,
                    "error_message": "Max iterations reached. Loop protection stopped execution.",
                    "started_at": now_iso(),
                    "ended_at": now_iso(),
                }
            )
            break

        step = step_map.get(current_step_id)
        if not step:
            status = "failed"
            failed_step_id = current_step_id
            logs.append(
                {
                    "step_id": current_step_id,
                    "step_name": "Unknown",
                    "step_type": "task",
                    "metadata": {},
                    "evaluated_rules": [],
                    "selected_next_step": None,
                    "selected_next_step_name": None,
                    "status": "failed",
                    "approver_id": None,
                    "error_message": "Step not found in workflow version.",
                    "started_at": now_iso(),
                    "ended_at": now_iso(),
                }
            )
            break

        if step["step_type"] == "approval":
            assigned_email = step.get("metadata", {}).get("assignee_email")
            logs.append(
                {
                    "step_id": step["id"],
                    "step_name": step["name"],
                    "step_type": step["step_type"],
                    "metadata": step["metadata"],
                    "evaluated_rules": [],
                    "selected_next_step": None,
                    "selected_next_step_name": None,
                    "status": "pending_approval",
                    "approver_id": None,
                    "assigned_to": assigned_email,
                    "error_message": None,
                    "started_at": now_iso(),
                    "ended_at": None,
                }
            )
            break

        log_entry, next_step_id = run_step(step, rules_map.get(step["id"], []), payload, triggered_by)
        if next_step_id:
            next_step = step_map.get(next_step_id)
            log_entry["selected_next_step_name"] = next_step["name"] if next_step else "Unknown"
        logs.append(log_entry)

        if log_entry["status"] == "failed" and not next_step_id:
            status = "failed"
            failed_step_id = step["id"]
            break

        current_step_id = next_step_id

    if status == "in_progress" and current_step_id and step_map.get(current_step_id, {}).get("step_type") == "approval":
        status = "in_progress"
    elif status == "in_progress":
        status = "completed"

    execution = {
        "id": execution_id,
        "workflow_id": workflow["id"],
        "workflow_name": workflow["name"],
        "workflow_version": workflow["version"],
        "status": status,
        "data": payload,
        "logs": logs,
        "current_step_id": failed_step_id or (current_step_id if status == "in_progress" else None),
        "retries": retries,
        "triggered_by": triggered_by,
        "started_at": started_at,
        "ended_at": None if status == "in_progress" else now_iso(),
    }
    db["executions"].append(execution)
    return execution


def continue_execution_from_step(db, workflow, execution, start_step_id, acting_user_id):
    steps = get_steps_for_workflow(db, workflow["id"])
    step_map = {step["id"]: step for step in steps}
    rules_map = {step["id"]: get_rules_for_step(db, step["id"]) for step in steps}
    current_step_id = start_step_id
    iterations = 0

    while current_step_id:
        iterations += 1
        if iterations > workflow.get("max_iterations", DEFAULT_MAX_ITERATIONS):
            execution["status"] = "failed"
            execution["current_step_id"] = current_step_id
            execution["ended_at"] = now_iso()
            execution["logs"].append(
                {
                    "step_id": current_step_id,
                    "step_name": step_map.get(current_step_id, {}).get("name", "Unknown"),
                    "step_type": step_map.get(current_step_id, {}).get("step_type", "task"),
                    "metadata": {},
                    "evaluated_rules": [],
                    "selected_next_step": None,
                    "selected_next_step_name": None,
                    "status": "failed",
                    "approver_id": None,
                    "error_message": "Max iterations reached. Loop protection stopped execution.",
                    "started_at": now_iso(),
                    "ended_at": now_iso(),
                }
            )
            return execution

        step = step_map.get(current_step_id)
        if not step:
            execution["status"] = "failed"
            execution["current_step_id"] = current_step_id
            execution["ended_at"] = now_iso()
            return execution

        if step["step_type"] == "approval":
            execution["status"] = "in_progress"
            execution["current_step_id"] = step["id"]
            execution["ended_at"] = None
            execution["logs"].append(
                {
                    "step_id": step["id"],
                    "step_name": step["name"],
                    "step_type": step["step_type"],
                    "metadata": step["metadata"],
                    "evaluated_rules": [],
                    "selected_next_step": None,
                    "selected_next_step_name": None,
                    "status": "pending_approval",
                    "approver_id": None,
                    "assigned_to": step.get("metadata", {}).get("assignee_email"),
                    "error_message": None,
                    "started_at": now_iso(),
                    "ended_at": None,
                }
            )
            return execution

        log_entry, next_step_id = run_step(step, rules_map.get(step["id"], []), execution["data"], acting_user_id)
        if next_step_id:
            next_step = step_map.get(next_step_id)
            log_entry["selected_next_step_name"] = next_step["name"] if next_step else "Unknown"
        execution["logs"].append(log_entry)

        if log_entry["status"] == "failed" and not next_step_id:
            execution["status"] = "failed"
            execution["current_step_id"] = step["id"]
            execution["ended_at"] = now_iso()
            return execution

        current_step_id = next_step_id

    execution["status"] = "completed"
    execution["current_step_id"] = None
    execution["ended_at"] = now_iso()
    return execution


def serialize_workflow_detail(db, workflow_id):
    bundle = get_workflow_bundle(db, workflow_id)
    if not bundle:
        return None
    workflow = deepcopy(bundle["workflow"])
    workflow["steps"] = []
    for step in bundle["steps"]:
        step_copy = deepcopy(step)
        step_copy["rules"] = deepcopy(bundle["rules_by_step"][step["id"]])
        workflow["steps"].append(step_copy)
    return workflow


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    db = load_db()
    return find_user_by_id(db, user_id)


def require_login(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login_page", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def can_approve_step(user, step):
    if not user or step["step_type"] != "approval":
        return False

    assigned_email = step.get("metadata", {}).get("assignee_email", "").lower()
    return user["email"].lower() == assigned_email or user.get("role") == "admin"


def pending_approval_summary(db, user):
    if not user:
        return []

    pending_items = []
    for execution in db["executions"]:
        if execution["status"] != "in_progress":
            continue
        current_step_id = execution.get("current_step_id")
        if not current_step_id:
            continue
        step = find_step(db, current_step_id)
        if not step or not can_approve_step(user, step):
            continue
        pending_items.append(
            {
                "execution": execution,
                "step": step,
                "workflow": find_workflow(db, execution["workflow_id"]),
            }
        )
    pending_items.sort(key=lambda item: item["execution"]["started_at"], reverse=True)
    return pending_items


@app.route("/style.css")
def serve_css():
    return Response(css_content, mimetype="text/css")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    db = load_db()
    error = request.args.get("error", "")
    next_url = request.args.get("next", "/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        next_url = request.form.get("next", "/")
        user = find_user_by_username(db, username)
        if not user or user["password"] != password:
            error = "Invalid username or password."
        else:
            session["user_id"] = user["id"]
            return redirect(next_url or url_for("home"))

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Login</title>
      <link rel="stylesheet" href="{{ url_for('serve_css') }}">
    </head>
    <body class="login-body">
      <div class="login-orb orb-one"></div>
      <div class="login-orb orb-two"></div>
      <main class="login-shell">
        <section class="login-card">
          <p class="eyebrow">Secure Access</p>
          <h1>Sign in to approve and manage workflows.</h1>
          <p class="hero-text">Each person gets their own login, and approval steps unlock only for the assigned approver.</p>
          {% if error %}
          <p class="error-banner">{{ error }}</p>
          {% endif %}
          <form class="stack-form" method="post" action="{{ url_for('login_page') }}">
            <input type="hidden" name="next" value="{{ next_url }}">
            <label>
              <span>Username</span>
              <input type="text" name="username" placeholder="manager" required>
            </label>
            <label>
              <span>Password</span>
              <input type="password" name="password" placeholder="manager123" required>
            </label>
            <button class="btn primary wide" type="submit">Login</button>
          </form>
        </section>
        <section class="login-sidekick">
          <p class="eyebrow">Demo Users</p>
          <div class="login-users">
            {% for user in users %}
            <article class="user-chip">
              <strong>{{ user.name }}</strong>
              <p>{{ user.role }} · {{ user.username }} / {{ user.password }}</p>
            </article>
            {% endfor %}
          </div>
        </section>
      </main>
    </body>
    </html>
    """
    return render_template_string(template, error=error, next_url=next_url, users=db["users"])


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/")
@require_login
def home():
    db = load_db()
    user = current_user()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = max(int(request.args.get("per_page", 10)), 1)
    search = request.args.get("search", "").strip()
    workflows, total = list_latest_workflows(db, search=search, page=page, per_page=per_page)
    executions = sorted(db["executions"], key=lambda item: item["started_at"], reverse=True)[:12]
    workflow_cards = []
    for workflow in workflows:
        steps = get_steps_for_workflow(db, workflow["id"])
        workflow_cards.append({"workflow": workflow, "steps_count": len(steps)})
    pending_approvals = pending_approval_summary(db, user)

    return render_template_string(
        DASHBOARD_TEMPLATE,
        user=user,
        workflow_cards=workflow_cards,
        executions=executions,
        pending_approvals=pending_approvals,
        search=search,
        page=page,
        per_page=per_page,
        total=total,
        has_prev=page > 1,
        has_next=page * per_page < total,
        default_schema=json.dumps(
            {
                "amount": {"type": "number", "required": True},
                "country": {"type": "string", "required": True},
                "department": {"type": "string", "required": False},
                "priority": {
                    "type": "string",
                    "required": True,
                    "allowed_values": ["High", "Medium", "Low"],
                },
            },
            indent=2,
        ),
    )


@app.route("/workflows/<workflow_id>/detail")
@require_login
def workflow_detail_page(workflow_id):
    db = load_db()
    user = current_user()
    bundle = get_workflow_bundle(db, workflow_id)
    if not bundle:
        return redirect(url_for("home"))

    executions = [
        execution
        for execution in db["executions"]
        if execution["workflow_id"] == workflow_id
    ]
    executions.sort(key=lambda item: item["started_at"], reverse=True)
    step_name_map = {step["id"]: step["name"] for step in bundle["steps"]}

    return render_template_string(
        WORKFLOW_DETAIL_TEMPLATE,
        user=user,
        workflow=bundle["workflow"],
        steps=bundle["steps"],
        rules_by_step=bundle["rules_by_step"],
        executions=executions[:12],
        step_name_map=step_name_map,
        schema_example=json.dumps(bundle["workflow"]["input_schema"], indent=2),
    )


@app.route("/executions/<execution_id>/view")
@require_login
def execution_detail_page(execution_id):
    db = load_db()
    user = current_user()
    execution = find_execution(db, execution_id)
    if not execution:
        return redirect(url_for("home"))
    workflow = find_workflow(db, execution["workflow_id"])
    current_step = find_step(db, execution.get("current_step_id")) if execution.get("current_step_id") else None
    can_approve = bool(current_step and can_approve_step(user, current_step) and execution["status"] == "in_progress")

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Execution {{ execution.id }}</title>
      <link rel="stylesheet" href="{{ url_for('serve_css') }}">
    </head>
    <body>
      <div class="page-shell">
        <div class="hero compact">
          <div>
            <a class="subtle-link" href="{{ back_href }}">Back to workflow</a>
            <h1>Execution Log</h1>
            <p>{{ execution.workflow_name }} v{{ execution.workflow_version }} · {{ execution.status }}</p>
          </div>
        </div>
        <div class="grid single">
          <section class="panel">
            <h2>Summary</h2>
            <div class="kv-grid">
              <div><span>Execution ID</span><strong>{{ execution.id }}</strong></div>
              <div><span>Triggered By</span><strong>{{ execution.triggered_by }}</strong></div>
              <div><span>Started</span><strong>{{ execution.started_at }}</strong></div>
              <div><span>Ended</span><strong>{{ execution.ended_at }}</strong></div>
            </div>
            {% if can_approve %}
            <div class="approval-banner">
              <div>
                <span>Approval Required</span>
                <strong>{{ current_step.name }}</strong>
              </div>
              <form method="post" action="{{ url_for('approve_execution_step', execution_id=execution.id) }}">
                <button class="btn primary" type="submit">Approve Step</button>
              </form>
            </div>
            {% endif %}
            <pre>{{ execution.data | tojson(indent=2) }}</pre>
          </section>
          <section class="panel">
            <h2>Step Logs</h2>
            {% for log in execution.logs %}
            <article class="log-card">
              <div class="log-head">
                <h3>{{ loop.index }}. {{ log.step_name }}</h3>
                <span class="pill {{ log.status }}">{{ log.status }}</span>
              </div>
              <p>{{ log.step_type }}{% if log.selected_next_step_name %} -> {{ log.selected_next_step_name }}{% endif %}</p>
              {% if log.error_message %}
              <p class="error-text">{{ log.error_message }}</p>
              {% endif %}
              <pre>{{ log | tojson(indent=2) }}</pre>
            </article>
            {% endfor %}
          </section>
        </div>
      </div>
    </body>
    </html>
    """
    back_href = url_for("workflow_detail_page", workflow_id=workflow["id"]) if workflow else url_for("home")
    return render_template_string(
        template,
        execution=execution,
        back_href=back_href,
        can_approve=can_approve,
        current_step=current_step,
    )


@app.route("/ui/workflows/create", methods=["POST"])
@require_login
def ui_create_workflow():
    db = load_db()
    try:
        schema = normalize_schema(parse_schema(request.form.get("input_schema", "{}")))
    except (json.JSONDecodeError, ValueError) as exc:
        return json_error(str(exc))

    created_at = now_iso()
    workflow_id = new_id()
    workflow = {
        "id": workflow_id,
        "workflow_key": workflow_id,
        "name": request.form.get("name", "Untitled Workflow").strip() or "Untitled Workflow",
        "description": request.form.get("description", "").strip(),
        "version": 1,
        "is_active": True,
        "input_schema": schema,
        "start_step_id": "",
        "max_iterations": int(request.form.get("max_iterations", DEFAULT_MAX_ITERATIONS)),
        "created_at": created_at,
        "updated_at": created_at,
    }
    db["workflows"].append(workflow)
    save_db(db)
    return redirect(url_for("workflow_detail_page", workflow_id=workflow_id))


@app.route("/ui/workflows/<workflow_id>/update", methods=["POST"])
@require_login
def ui_update_workflow(workflow_id):
    db = load_db()
    try:
        schema = normalize_schema(parse_schema(request.form.get("input_schema", "{}")))
        workflow = clone_workflow_version(
            db,
            workflow_id,
            {
                "name": request.form.get("name", "").strip() or "Untitled Workflow",
                "description": request.form.get("description", "").strip(),
                "input_schema": schema,
                "max_iterations": int(request.form.get("max_iterations", DEFAULT_MAX_ITERATIONS)),
            },
        )
        save_db(db)
    except (ValueError, json.JSONDecodeError) as exc:
        return json_error(str(exc))
    return redirect(url_for("workflow_detail_page", workflow_id=workflow["id"]))


@app.route("/ui/workflows/<workflow_id>/delete", methods=["POST"])
@require_login
def ui_delete_workflow(workflow_id):
    db = load_db()
    delete_workflow_family(db, workflow_id)
    save_db(db)
    return redirect(url_for("home"))


@app.route("/ui/workflows/<workflow_id>/steps/create", methods=["POST"])
@require_login
def ui_create_step(workflow_id):
    db = load_db()
    workflow = find_workflow(db, workflow_id)
    if not workflow:
        return json_error("Workflow not found.", 404)

    step_type = request.form.get("step_type", "task")
    if step_type not in STEP_TYPES:
        return json_error("Unsupported step type.")

    created_at = now_iso()
    step = {
        "id": new_id(),
        "workflow_id": workflow_id,
        "name": request.form.get("name", "Untitled Step").strip() or "Untitled Step",
        "step_type": step_type,
        "order": int(request.form.get("order", 1)),
        "metadata": parse_metadata(request.form.get("metadata", "{}")),
        "created_at": created_at,
        "updated_at": created_at,
    }
    db["steps"].append(step)
    if not workflow.get("start_step_id"):
        workflow["start_step_id"] = step["id"]
        workflow["updated_at"] = now_iso()
    save_db(db)
    return redirect(url_for("workflow_detail_page", workflow_id=workflow_id))


@app.route("/ui/steps/<step_id>/update", methods=["POST"])
@require_login
def ui_update_step(step_id):
    db = load_db()
    step = find_step(db, step_id)
    if not step:
        return json_error("Step not found.", 404)

    step_type = request.form.get("step_type", step["step_type"])
    if step_type not in STEP_TYPES:
        return json_error("Unsupported step type.")

    step["name"] = request.form.get("name", step["name"]).strip() or step["name"]
    step["step_type"] = step_type
    step["order"] = int(request.form.get("order", step["order"]))
    step["metadata"] = parse_metadata(request.form.get("metadata", json.dumps(step["metadata"])))
    step["updated_at"] = now_iso()
    save_db(db)
    return redirect(url_for("workflow_detail_page", workflow_id=step["workflow_id"]))


@app.route("/ui/steps/<step_id>/delete", methods=["POST"])
@require_login
def ui_delete_step(step_id):
    db = load_db()
    step = find_step(db, step_id)
    if not step:
        return redirect(url_for("home"))

    workflow = find_workflow(db, step["workflow_id"])
    db["steps"] = [item for item in db["steps"] if item["id"] != step_id]
    db["rules"] = [
        rule for rule in db["rules"] if rule["step_id"] != step_id and rule["next_step_id"] != step_id
    ]
    if workflow and workflow.get("start_step_id") == step_id:
        remaining_steps = get_steps_for_workflow(db, workflow["id"])
        workflow["start_step_id"] = remaining_steps[0]["id"] if remaining_steps else ""
        workflow["updated_at"] = now_iso()
    save_db(db)
    return redirect(url_for("workflow_detail_page", workflow_id=step["workflow_id"]))


@app.route("/ui/workflows/<workflow_id>/start-step", methods=["POST"])
@require_login
def ui_set_start_step(workflow_id):
    db = load_db()
    workflow = find_workflow(db, workflow_id)
    if not workflow:
        return json_error("Workflow not found.", 404)
    workflow["start_step_id"] = request.form.get("start_step_id", "")
    workflow["updated_at"] = now_iso()
    save_db(db)
    return redirect(url_for("workflow_detail_page", workflow_id=workflow_id))


@app.route("/ui/steps/<step_id>/rules/create", methods=["POST"])
@require_login
def ui_create_rule(step_id):
    db = load_db()
    step = find_step(db, step_id)
    if not step:
        return json_error("Step not found.", 404)

    created_at = now_iso()
    next_step_id = request.form.get("next_step_id") or None
    rule = {
        "id": new_id(),
        "step_id": step_id,
        "condition": request.form.get("condition", "DEFAULT").strip() or "DEFAULT",
        "next_step_id": next_step_id,
        "priority": int(request.form.get("priority", 1)),
        "created_at": created_at,
        "updated_at": created_at,
    }
    db["rules"].append(rule)
    save_db(db)
    return redirect(url_for("workflow_detail_page", workflow_id=step["workflow_id"]))


@app.route("/ui/rules/<rule_id>/update", methods=["POST"])
@require_login
def ui_update_rule(rule_id):
    db = load_db()
    rule = find_rule(db, rule_id)
    if not rule:
        return json_error("Rule not found.", 404)

    step = find_step(db, rule["step_id"])
    rule["condition"] = request.form.get("condition", rule["condition"]).strip() or "DEFAULT"
    rule["next_step_id"] = request.form.get("next_step_id") or None
    rule["priority"] = int(request.form.get("priority", rule["priority"]))
    rule["updated_at"] = now_iso()
    save_db(db)
    return redirect(url_for("workflow_detail_page", workflow_id=step["workflow_id"]))


@app.route("/ui/rules/<rule_id>/delete", methods=["POST"])
@require_login
def ui_delete_rule(rule_id):
    db = load_db()
    rule = find_rule(db, rule_id)
    if not rule:
        return redirect(url_for("home"))
    step = find_step(db, rule["step_id"])
    db["rules"] = [item for item in db["rules"] if item["id"] != rule_id]
    save_db(db)
    return redirect(url_for("workflow_detail_page", workflow_id=step["workflow_id"]))


@app.route("/ui/workflows/<workflow_id>/execute", methods=["POST"])
@require_login
def ui_execute_workflow(workflow_id):
    db = load_db()
    workflow = find_workflow(db, workflow_id)
    if not workflow:
        return json_error("Workflow not found.", 404)

    try:
        payload = form_payload_from_schema(workflow["input_schema"], request.form)
        execution = execute_workflow_internal(
            db,
            workflow,
            payload,
            triggered_by=request.form.get("triggered_by", "ui-user"),
        )
        save_db(db)
    except ValueError as exc:
        return json_error(str(exc))
    return redirect(url_for("execution_detail_page", execution_id=execution["id"]))


@app.route("/ui/executions/<execution_id>/retry", methods=["POST"])
@require_login
def ui_retry_execution(execution_id):
    db = load_db()
    execution = find_execution(db, execution_id)
    if not execution:
        return json_error("Execution not found.", 404)
    if execution["status"] != "failed":
        return json_error("Only failed executions can be retried.")

    workflow = find_workflow(db, execution["workflow_id"])
    if not workflow:
        return json_error("Workflow not found for this execution.", 404)

    successful_logs = [log for log in execution["logs"] if log["status"] == "completed"]
    failed_step_id = execution.get("current_step_id")
    if not failed_step_id:
        return json_error("No failed step available for retry.")

    try:
        new_execution = execute_workflow_internal(
            db,
            workflow,
            execution["data"],
            triggered_by=execution["triggered_by"],
            resume_from_step_id=failed_step_id,
            existing_logs=successful_logs,
            retries=execution.get("retries", 0) + 1,
        )
        save_db(db)
    except ValueError as exc:
        return json_error(str(exc))
    return redirect(url_for("execution_detail_page", execution_id=new_execution["id"]))


@app.route("/executions/<execution_id>/approve", methods=["POST"])
@require_login
def approve_execution_step(execution_id):
    db = load_db()
    user = current_user()
    execution = find_execution(db, execution_id)
    if not execution:
        return json_error("Execution not found.", 404)
    if execution["status"] != "in_progress" or not execution.get("current_step_id"):
        return json_error("This execution is not waiting for approval.")

    workflow = find_workflow(db, execution["workflow_id"])
    step = find_step(db, execution["current_step_id"])
    if not workflow or not step:
        return json_error("Approval step could not be resolved.", 404)
    if not can_approve_step(user, step):
        return json_error("You are not allowed to approve this step.", 403)

    pending_log = next(
        (
            log
            for log in reversed(execution["logs"])
            if log["step_id"] == step["id"] and log["status"] == "pending_approval"
        ),
        None,
    )
    if not pending_log:
        return json_error("Pending approval log not found.", 404)

    rule_outcome = evaluate_step_rules(get_rules_for_step(db, step["id"]), execution["data"])
    next_step_id = rule_outcome["next_step_id"]
    next_step = find_step(db, next_step_id) if next_step_id else None

    pending_log["evaluated_rules"] = rule_outcome["evaluated_rules"]
    pending_log["selected_next_step"] = next_step_id
    pending_log["selected_next_step_name"] = next_step["name"] if next_step else None
    pending_log["status"] = "completed" if next_step_id or rule_outcome["matched_rule"] else "failed"
    pending_log["approver_id"] = user["id"]
    pending_log["approved_by_name"] = user["name"]
    pending_log["error_message"] = rule_outcome["error_message"]
    pending_log["ended_at"] = now_iso()

    if pending_log["status"] == "failed" and not next_step_id:
        execution["status"] = "failed"
        execution["current_step_id"] = step["id"]
        execution["ended_at"] = now_iso()
    else:
        continue_execution_from_step(db, workflow, execution, next_step_id, user["id"])

    save_db(db)
    return redirect(url_for("execution_detail_page", execution_id=execution_id))


@app.route("/workflows", methods=["POST"])
def create_workflow():
    db = load_db()
    payload = get_json_payload()
    try:
        schema = normalize_schema(payload.get("input_schema", {}))
    except ValueError as exc:
        return json_error(str(exc))

    created_at = now_iso()
    workflow_id = new_id()
    workflow = {
        "id": workflow_id,
        "workflow_key": workflow_id,
        "name": payload.get("name", "Untitled Workflow"),
        "description": payload.get("description", ""),
        "version": 1,
        "is_active": True,
        "input_schema": schema,
        "start_step_id": payload.get("start_step_id", ""),
        "max_iterations": int(payload.get("max_iterations", DEFAULT_MAX_ITERATIONS)),
        "created_at": created_at,
        "updated_at": created_at,
    }
    db["workflows"].append(workflow)
    save_db(db)
    return jsonify(workflow), 201


@app.route("/workflows", methods=["GET"])
def list_workflows():
    db = load_db()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = max(int(request.args.get("per_page", 10)), 1)
    search = request.args.get("search", "").strip()
    workflows, total = list_latest_workflows(db, search=search, page=page, per_page=per_page)
    return jsonify(
        {
            "items": workflows,
            "page": page,
            "per_page": per_page,
            "total": total,
        }
    )


@app.route("/workflows/<workflow_id>", methods=["GET"])
def get_workflow(workflow_id):
    db = load_db()
    workflow = serialize_workflow_detail(db, workflow_id)
    if not workflow:
        return json_error("Workflow not found.", 404)
    return jsonify(workflow)


@app.route("/workflows/<workflow_id>", methods=["PUT"])
def update_workflow(workflow_id):
    db = load_db()
    payload = get_json_payload()
    updates = {}

    if "name" in payload:
        updates["name"] = payload["name"]
    if "description" in payload:
        updates["description"] = payload["description"]
    if "input_schema" in payload:
        try:
            updates["input_schema"] = normalize_schema(payload["input_schema"])
        except ValueError as exc:
            return json_error(str(exc))
    if "max_iterations" in payload:
        updates["max_iterations"] = int(payload["max_iterations"])

    try:
        workflow = clone_workflow_version(db, workflow_id, updates)
    except ValueError as exc:
        return json_error(str(exc), 404)
    save_db(db)
    return jsonify(workflow)


@app.route("/workflows/<workflow_id>", methods=["DELETE"])
def delete_workflow(workflow_id):
    db = load_db()
    deleted = delete_workflow_family(db, workflow_id)
    if not deleted:
        return json_error("Workflow not found.", 404)
    save_db(db)
    return jsonify({"deleted": True})


@app.route("/workflows/<workflow_id>/steps", methods=["POST"])
def create_step(workflow_id):
    db = load_db()
    workflow = find_workflow(db, workflow_id)
    if not workflow:
        return json_error("Workflow not found.", 404)

    payload = get_json_payload()
    step_type = payload.get("step_type", "task")
    if step_type not in STEP_TYPES:
        return json_error("Unsupported step type.")

    created_at = now_iso()
    step = {
        "id": new_id(),
        "workflow_id": workflow_id,
        "name": payload.get("name", "Untitled Step"),
        "step_type": step_type,
        "order": int(payload.get("order", 1)),
        "metadata": parse_metadata(payload.get("metadata")),
        "created_at": created_at,
        "updated_at": created_at,
    }
    db["steps"].append(step)
    if not workflow.get("start_step_id"):
        workflow["start_step_id"] = step["id"]
        workflow["updated_at"] = now_iso()
    save_db(db)
    return jsonify(step), 201


@app.route("/workflows/<workflow_id>/steps", methods=["GET"])
def list_steps(workflow_id):
    db = load_db()
    if not find_workflow(db, workflow_id):
        return json_error("Workflow not found.", 404)
    return jsonify(get_steps_for_workflow(db, workflow_id))


@app.route("/steps/<step_id>", methods=["PUT"])
def update_step(step_id):
    db = load_db()
    step = find_step(db, step_id)
    if not step:
        return json_error("Step not found.", 404)

    payload = get_json_payload()
    if "name" in payload:
        step["name"] = payload["name"]
    if "step_type" in payload:
        if payload["step_type"] not in STEP_TYPES:
            return json_error("Unsupported step type.")
        step["step_type"] = payload["step_type"]
    if "order" in payload:
        step["order"] = int(payload["order"])
    if "metadata" in payload:
        step["metadata"] = parse_metadata(payload["metadata"])
    step["updated_at"] = now_iso()
    save_db(db)
    return jsonify(step)


@app.route("/steps/<step_id>", methods=["DELETE"])
def delete_step(step_id):
    db = load_db()
    step = find_step(db, step_id)
    if not step:
        return json_error("Step not found.", 404)

    workflow = find_workflow(db, step["workflow_id"])
    db["steps"] = [item for item in db["steps"] if item["id"] != step_id]
    db["rules"] = [rule for rule in db["rules"] if rule["step_id"] != step_id and rule["next_step_id"] != step_id]
    if workflow and workflow.get("start_step_id") == step_id:
        remaining = get_steps_for_workflow(db, workflow["id"])
        workflow["start_step_id"] = remaining[0]["id"] if remaining else ""
        workflow["updated_at"] = now_iso()
    save_db(db)
    return jsonify({"deleted": True})


@app.route("/steps/<step_id>/rules", methods=["POST"])
def create_rule(step_id):
    db = load_db()
    step = find_step(db, step_id)
    if not step:
        return json_error("Step not found.", 404)

    payload = get_json_payload()
    created_at = now_iso()
    rule = {
        "id": new_id(),
        "step_id": step_id,
        "condition": payload.get("condition", "DEFAULT"),
        "next_step_id": payload.get("next_step_id"),
        "priority": int(payload.get("priority", 1)),
        "created_at": created_at,
        "updated_at": created_at,
    }
    db["rules"].append(rule)
    save_db(db)
    return jsonify(rule), 201


@app.route("/steps/<step_id>/rules", methods=["GET"])
def list_rules(step_id):
    db = load_db()
    if not find_step(db, step_id):
        return json_error("Step not found.", 404)
    return jsonify(get_rules_for_step(db, step_id))


@app.route("/rules/<rule_id>", methods=["PUT"])
def update_rule(rule_id):
    db = load_db()
    rule = find_rule(db, rule_id)
    if not rule:
        return json_error("Rule not found.", 404)

    payload = get_json_payload()
    if "condition" in payload:
        rule["condition"] = payload["condition"]
    if "next_step_id" in payload:
        rule["next_step_id"] = payload["next_step_id"]
    if "priority" in payload:
        rule["priority"] = int(payload["priority"])
    rule["updated_at"] = now_iso()
    save_db(db)
    return jsonify(rule)


@app.route("/rules/<rule_id>", methods=["DELETE"])
def delete_rule(rule_id):
    db = load_db()
    if not find_rule(db, rule_id):
        return json_error("Rule not found.", 404)
    db["rules"] = [item for item in db["rules"] if item["id"] != rule_id]
    save_db(db)
    return jsonify({"deleted": True})


@app.route("/workflows/<workflow_id>/execute", methods=["POST"])
def execute_workflow(workflow_id):
    db = load_db()
    workflow = find_workflow(db, workflow_id)
    if not workflow:
        return json_error("Workflow not found.", 404)

    payload = get_json_payload()
    try:
        execution = execute_workflow_internal(
            db,
            workflow,
            payload,
            triggered_by=payload.get("triggered_by", "api-user"),
        )
    except ValueError as exc:
        return json_error(str(exc))

    save_db(db)
    return jsonify(execution), 201


@app.route("/executions/<execution_id>", methods=["GET"])
def get_execution(execution_id):
    db = load_db()
    execution = find_execution(db, execution_id)
    if not execution:
        return json_error("Execution not found.", 404)
    return jsonify(execution)


@app.route("/executions/<execution_id>/cancel", methods=["POST"])
def cancel_execution(execution_id):
    db = load_db()
    execution = find_execution(db, execution_id)
    if not execution:
        return json_error("Execution not found.", 404)
    if execution["status"] in {"completed", "failed"}:
        return json_error("Only pending or in-progress executions can be canceled.")
    execution["status"] = "canceled"
    execution["ended_at"] = now_iso()
    save_db(db)
    return jsonify(execution)


@app.route("/executions/<execution_id>/retry", methods=["POST"])
def retry_execution(execution_id):
    db = load_db()
    execution = find_execution(db, execution_id)
    if not execution:
        return json_error("Execution not found.", 404)
    if execution["status"] != "failed":
        return json_error("Only failed executions can be retried.")

    workflow = find_workflow(db, execution["workflow_id"])
    if not workflow:
        return json_error("Workflow not found for this execution.", 404)

    successful_logs = [log for log in execution["logs"] if log["status"] == "completed"]
    failed_step_id = execution.get("current_step_id")
    if not failed_step_id:
        return json_error("No failed step available for retry.")

    try:
        new_execution = execute_workflow_internal(
            db,
            workflow,
            execution["data"],
            triggered_by=execution["triggered_by"],
            resume_from_step_id=failed_step_id,
            existing_logs=successful_logs,
            retries=execution.get("retries", 0) + 1,
        )
    except ValueError as exc:
        return json_error(str(exc))

    save_db(db)
    return jsonify(new_execution), 201


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=4444)
