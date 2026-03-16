DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Halleyx Workflow Engine</title>
  <link rel="stylesheet" href="{{ url_for('serve_css') }}">
</head>
<body>
  <div class="ambient ambient-a"></div>
  <div class="ambient ambient-b"></div>
  <div class="page-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Workflow Command Center</p>
        <h1 class="brand-title">Halleyx Project</h1>
      </div>
      <div class="user-bar">
        <div class="user-badge">
          <span>Signed in</span>
          <strong>{{ user.name }}</strong>
          <p>{{ user.role }} · {{ user.email }}</p>
        </div>
        <form method="post" action="{{ url_for('logout') }}">
          <button class="btn secondary" type="submit">Logout</button>
        </form>
      </div>
    </header>

    <header class="hero">
      <div class="hero-copy cinematic">
        <p class="eyebrow">Live Operations</p>
        <h1>Design, launch, and approve workflows from one animated workspace.</h1>
        <p class="hero-text">Create process definitions, hand off approvals to the right person, and watch execution state move in real time through the audit stream.</p>
      </div>
      <div class="hero-card floating-card">
        <div>
          <span>Total Workflows</span>
          <strong>{{ total }}</strong>
        </div>
        <div>
          <span>Recent Executions</span>
          <strong>{{ executions|length }}</strong>
        </div>
        <div>
          <span>Pending For You</span>
          <strong>{{ pending_approvals|length }}</strong>
        </div>
      </div>
    </header>

    <section class="panel highlight-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Approvals Queue</p>
          <h2>Items waiting for {{ user.name }}</h2>
        </div>
      </div>
      {% if pending_approvals %}
      <div class="approval-grid">
        {% for item in pending_approvals %}
        <article class="approval-card">
          <div>
            <p class="eyebrow">Needs Action</p>
            <h3>{{ item.workflow.name }}</h3>
            <p>{{ item.step.name }} · Execution {{ item.execution.id }}</p>
          </div>
          <div class="inline-actions">
            <a class="btn tiny" href="{{ url_for('execution_detail_page', execution_id=item.execution.id) }}">Open Execution</a>
            <form method="post" action="{{ url_for('approve_execution_step', execution_id=item.execution.id) }}">
              <button class="btn tiny primary" type="submit">Approve</button>
            </form>
          </div>
        </article>
        {% endfor %}
      </div>
      {% else %}
      <p class="empty-state">No approvals are waiting for you right now.</p>
      {% endif %}
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Create Workflow</p>
          <h2>Start a new process definition</h2>
        </div>
      </div>
      <form class="form-grid" method="post" action="{{ url_for('ui_create_workflow') }}">
        <label>
          <span>Name</span>
          <input type="text" name="name" placeholder="Expense Approval" required>
        </label>
        <label>
          <span>Max Iterations</span>
          <input type="number" name="max_iterations" min="1" value="15">
        </label>
        <label class="full">
          <span>Description</span>
          <textarea name="description" rows="2" placeholder="What this workflow does"></textarea>
        </label>
        <label class="full">
          <span>Input Schema JSON</span>
          <textarea name="input_schema" rows="12">{{ default_schema }}</textarea>
        </label>
        <div class="full form-actions">
          <button class="btn primary" type="submit">Create Workflow</button>
        </div>
      </form>
    </section>

    <section class="panel">
      <div class="panel-head spread">
        <div>
          <p class="eyebrow">Workflow List</p>
          <h2>Browse and manage saved workflows</h2>
        </div>
        <form class="search-bar" method="get" action="{{ url_for('home') }}">
          <input type="text" name="search" value="{{ search }}" placeholder="Search by id or name">
          <input type="hidden" name="page" value="1">
          <button class="btn secondary" type="submit">Search</button>
        </form>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Steps</th>
              <th>Version</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {% for item in workflow_cards %}
            <tr>
              <td class="mono">{{ item.workflow.id }}</td>
              <td>{{ item.workflow.name }}</td>
              <td>{{ item.steps_count }}</td>
              <td>{{ item.workflow.version }}</td>
              <td><span class="pill {{ 'active' if item.workflow.is_active else 'inactive' }}">{{ 'Active' if item.workflow.is_active else 'Inactive' }}</span></td>
              <td class="actions">
                <a class="btn tiny" href="{{ url_for('workflow_detail_page', workflow_id=item.workflow.id) }}">Open</a>
                <form method="post" action="{{ url_for('ui_delete_workflow', workflow_id=item.workflow.id) }}">
                  <button class="btn tiny danger" type="submit">Delete</button>
                </form>
              </td>
            </tr>
            {% else %}
            <tr>
              <td colspan="6">No workflows found.</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>

      <div class="pager">
        {% if has_prev %}
        <a class="btn secondary" href="{{ url_for('home', search=search, page=page-1, per_page=per_page) }}">Previous</a>
        {% endif %}
        <span>Page {{ page }}</span>
        {% if has_next %}
        <a class="btn secondary" href="{{ url_for('home', search=search, page=page+1, per_page=per_page) }}">Next</a>
        {% endif %}
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Audit Log</p>
          <h2>Latest executions</h2>
        </div>
      </div>
      <div class="audit-list">
        {% for execution in executions %}
        <article class="audit-row">
          <div>
            <strong>{{ execution.workflow_name }}</strong>
            <p class="mono">{{ execution.id }}</p>
          </div>
          <div>
            <span>Version</span>
            <strong>{{ execution.workflow_version }}</strong>
          </div>
          <div>
            <span>Status</span>
            <strong>{{ execution.status }}</strong>
          </div>
          <div>
            <span>Started</span>
            <strong>{{ execution.started_at }}</strong>
          </div>
          <a class="btn tiny" href="{{ url_for('execution_detail_page', execution_id=execution.id) }}">View Logs</a>
        </article>
        {% else %}
        <p class="empty-state">Run a workflow to populate the audit log.</p>
        {% endfor %}
      </div>
    </section>
  </div>
</body>
</html>
"""


WORKFLOW_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ workflow.name }}</title>
  <link rel="stylesheet" href="{{ url_for('serve_css') }}">
</head>
<body>
  <div class="ambient ambient-a"></div>
  <div class="ambient ambient-c"></div>
  <div class="page-shell">
    <header class="topbar">
      <div>
        <a class="subtle-link" href="{{ url_for('home') }}">Back to dashboard</a>
        <p class="eyebrow">Workflow Detail</p>
      </div>
      <div class="user-bar">
        <div class="user-badge">
          <span>Signed in</span>
          <strong>{{ user.name }}</strong>
          <p>{{ user.role }} · {{ user.email }}</p>
        </div>
        <form method="post" action="{{ url_for('logout') }}">
          <button class="btn secondary" type="submit">Logout</button>
        </form>
      </div>
    </header>

    <header class="hero compact">
      <div class="hero-copy cinematic">
        <h1>{{ workflow.name }}</h1>
        <p class="hero-text">Version {{ workflow.version }} · {{ 'Active' if workflow.is_active else 'Inactive' }} · Start step {{ step_name_map.get(workflow.start_step_id, 'Not set') }}</p>
      </div>
    </header>

    <div class="grid two-col">
      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Editor</p>
            <h2>Update workflow metadata</h2>
          </div>
        </div>
        <form class="form-grid" method="post" action="{{ url_for('ui_update_workflow', workflow_id=workflow.id) }}">
          <label>
            <span>Name</span>
            <input type="text" name="name" value="{{ workflow.name }}" required>
          </label>
          <label>
            <span>Max Iterations</span>
            <input type="number" name="max_iterations" min="1" value="{{ workflow.max_iterations }}">
          </label>
          <label class="full">
            <span>Description</span>
            <textarea name="description" rows="2">{{ workflow.description }}</textarea>
          </label>
          <label class="full">
            <span>Input Schema JSON</span>
            <textarea name="input_schema" rows="12">{{ schema_example }}</textarea>
          </label>
          <div class="full form-actions">
            <button class="btn primary" type="submit">Create New Version</button>
          </div>
        </form>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Execution</p>
            <h2>Run this workflow</h2>
          </div>
        </div>
        <form class="form-grid" method="post" action="{{ url_for('ui_execute_workflow', workflow_id=workflow.id) }}">
          <label class="full">
            <span>Triggered By</span>
            <input type="text" name="triggered_by" value="{{ user.username }}">
          </label>
          {% for field, config in workflow.input_schema.items() %}
          <label>
            <span>{{ field }}{% if config.required %} *{% endif %}</span>
            {% if config.allowed_values %}
            <select name="{{ field }}">
              <option value="">Select</option>
              {% for value in config.allowed_values %}
              <option value="{{ value }}">{{ value }}</option>
              {% endfor %}
            </select>
            {% elif config.type == 'boolean' %}
            <select name="{{ field }}">
              <option value="">Select</option>
              <option value="true">True</option>
              <option value="false">False</option>
            </select>
            {% else %}
            <input type="{{ 'number' if config.type == 'number' else 'text' }}" name="{{ field }}">
            {% endif %}
          </label>
          {% endfor %}
          <div class="full form-actions">
            <button class="btn primary" type="submit">Start Execution</button>
          </div>
        </form>

        <form class="stack-form start-step-form" method="post" action="{{ url_for('ui_set_start_step', workflow_id=workflow.id) }}">
          <label>
            <span>Start Step</span>
            <select name="start_step_id">
              <option value="">Select start step</option>
              {% for step in steps %}
              <option value="{{ step.id }}" {% if workflow.start_step_id == step.id %}selected{% endif %}>{{ step.name }}</option>
              {% endfor %}
            </select>
          </label>
          <button class="btn secondary" type="submit">Save Start Step</button>
        </form>
      </section>
    </div>

    <div class="grid two-col">
      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Steps</p>
            <h2>Add and edit workflow steps</h2>
          </div>
        </div>
        <form class="form-grid" method="post" action="{{ url_for('ui_create_step', workflow_id=workflow.id) }}">
          <label>
            <span>Step Name</span>
            <input type="text" name="name" placeholder="Manager Approval" required>
          </label>
          <label>
            <span>Step Type</span>
            <select name="step_type">
              <option value="task">Task</option>
              <option value="approval">Approval</option>
              <option value="notification">Notification</option>
            </select>
          </label>
          <label>
            <span>Order</span>
            <input type="number" name="order" min="1" value="{{ steps|length + 1 }}">
          </label>
          <label class="full">
            <span>Metadata JSON</span>
            <textarea name="metadata" rows="3">{}</textarea>
          </label>
          <div class="full form-actions">
            <button class="btn primary" type="submit">Add Step</button>
          </div>
        </form>

        <div class="stack-list">
          {% for step in steps %}
          <article class="stack-card">
            <div class="log-head">
              <h3>{{ step.order }}. {{ step.name }}</h3>
              <span class="pill neutral">{{ step.step_type }}</span>
            </div>
            <form class="form-grid compact-grid" method="post" action="{{ url_for('ui_update_step', step_id=step.id) }}">
              <label>
                <span>Name</span>
                <input type="text" name="name" value="{{ step.name }}">
              </label>
              <label>
                <span>Type</span>
                <select name="step_type">
                  <option value="task" {% if step.step_type == 'task' %}selected{% endif %}>Task</option>
                  <option value="approval" {% if step.step_type == 'approval' %}selected{% endif %}>Approval</option>
                  <option value="notification" {% if step.step_type == 'notification' %}selected{% endif %}>Notification</option>
                </select>
              </label>
              <label>
                <span>Order</span>
                <input type="number" name="order" value="{{ step.order }}">
              </label>
              <label class="full">
                <span>Metadata JSON</span>
                <textarea name="metadata" rows="3">{{ step.metadata | tojson(indent=2) }}</textarea>
              </label>
              <div class="full inline-actions">
                <button class="btn tiny" type="submit">Save Step</button>
              </div>
            </form>
            <form method="post" action="{{ url_for('ui_delete_step', step_id=step.id) }}">
              <button class="btn tiny danger" type="submit">Delete Step</button>
            </form>
          </article>
          {% else %}
          <p class="empty-state">Add your first step to begin designing the workflow.</p>
          {% endfor %}
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Rules</p>
            <h2>Define branching conditions by step</h2>
          </div>
        </div>

        {% if not steps %}
        <div class="empty-panel">
          <h3>No steps yet</h3>
          <p class="empty-state">Add at least one step first. The rules editor appears after steps exist because every rule belongs to a specific step.</p>
        </div>
        {% endif %}

        {% for step in steps %}
        <article class="rule-section">
          <div class="log-head">
            <h3>{{ step.name }}</h3>
            <span class="pill neutral">Step Rules</span>
          </div>
          <form class="form-grid compact-grid" method="post" action="{{ url_for('ui_create_rule', step_id=step.id) }}">
            <label class="full">
              <span>Condition</span>
              <input type="text" name="condition" placeholder="amount > 100 && country == 'US'">
            </label>
            <label>
              <span>Priority</span>
              <input type="number" name="priority" min="1" value="{{ (rules_by_step[step.id]|length) + 1 }}">
            </label>
            <label>
              <span>Next Step</span>
              <select name="next_step_id">
                <option value="">END</option>
                {% for next_step in steps %}
                <option value="{{ next_step.id }}">{{ next_step.name }}</option>
                {% endfor %}
              </select>
            </label>
            <div class="full form-actions">
              <button class="btn tiny" type="submit">Add Rule</button>
            </div>
          </form>

          <div class="stack-list slim">
            {% for rule in rules_by_step[step.id] %}
            <article class="stack-card">
              <form class="form-grid compact-grid" method="post" action="{{ url_for('ui_update_rule', rule_id=rule.id) }}">
                <label class="full">
                  <span>Condition</span>
                  <input type="text" name="condition" value="{{ rule.condition }}">
                </label>
                <label>
                  <span>Priority</span>
                  <input type="number" name="priority" value="{{ rule.priority }}">
                </label>
                <label>
                  <span>Next Step</span>
                  <select name="next_step_id">
                    <option value="" {% if not rule.next_step_id %}selected{% endif %}>END</option>
                    {% for next_step in steps %}
                    <option value="{{ next_step.id }}" {% if rule.next_step_id == next_step.id %}selected{% endif %}>{{ next_step.name }}</option>
                    {% endfor %}
                  </select>
                </label>
                <div class="full inline-actions">
                  <button class="btn tiny" type="submit">Save Rule</button>
                </div>
              </form>
              <form method="post" action="{{ url_for('ui_delete_rule', rule_id=rule.id) }}">
                <button class="btn tiny danger" type="submit">Delete Rule</button>
              </form>
            </article>
            {% else %}
            <p class="empty-state">No rules yet. Add at least one DEFAULT rule.</p>
            {% endfor %}
          </div>
        </article>
        {% endfor %}
      </section>
    </div>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Audit Trail</p>
          <h2>Recent executions for this workflow</h2>
        </div>
      </div>
      <div class="audit-list">
        {% for execution in executions %}
        <article class="audit-row">
          <div>
            <strong>{{ execution.id }}</strong>
            <p>Triggered by {{ execution.triggered_by }}</p>
          </div>
          <div>
            <span>Status</span>
            <strong>{{ execution.status }}</strong>
          </div>
          <div>
            <span>Started</span>
            <strong>{{ execution.started_at }}</strong>
          </div>
          <div class="actions">
            <a class="btn tiny" href="{{ url_for('execution_detail_page', execution_id=execution.id) }}">View Logs</a>
            {% if execution.status == 'failed' %}
            <form method="post" action="{{ url_for('ui_retry_execution', execution_id=execution.id) }}">
              <button class="btn tiny warning" type="submit">Retry</button>
            </form>
            {% endif %}
          </div>
        </article>
        {% else %}
        <p class="empty-state">This workflow has no executions yet.</p>
        {% endfor %}
      </div>
    </section>
  </div>
</body>
</html>
"""
