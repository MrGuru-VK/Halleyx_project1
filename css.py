css_content = """
:root {
    --bg: #07141f;
    --bg-mid: #102536;
    --bg-soft: #163a4d;
    --ink: #eef7f7;
    --muted: #9bb9bd;
    --panel: rgba(9, 23, 35, 0.72);
    --panel-strong: rgba(14, 32, 46, 0.92);
    --line: rgba(154, 230, 225, 0.14);
    --accent: #ff7a59;
    --accent-dark: #ff4f7a;
    --accent-soft: rgba(255, 122, 89, 0.18);
    --accent-cool: #49dcb1;
    --danger: #ff5a6b;
    --warning: #ffb347;
    --success: #32d296;
    --shadow: 0 24px 70px rgba(0, 0, 0, 0.28);
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    color: var(--ink);
    font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    background:
        radial-gradient(circle at top left, rgba(255, 79, 122, 0.24), transparent 26%),
        radial-gradient(circle at top right, rgba(73, 220, 177, 0.18), transparent 24%),
        radial-gradient(circle at bottom center, rgba(255, 122, 89, 0.18), transparent 22%),
        linear-gradient(140deg, var(--bg) 0%, var(--bg-mid) 48%, var(--bg-soft) 100%);
    min-height: 100vh;
    overflow-x: hidden;
}

body::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 34px 34px;
    mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
    opacity: 0.35;
    pointer-events: none;
}

.login-body {
    display: grid;
    place-items: center;
    min-height: 100vh;
}

.ambient,
.login-orb {
    position: fixed;
    border-radius: 999px;
    filter: blur(18px);
    z-index: -1;
    animation: drift 16s ease-in-out infinite;
}

.ambient-a,
.orb-one {
    top: -80px;
    left: -40px;
    width: 340px;
    height: 340px;
    background: radial-gradient(circle, rgba(255, 79, 122, 0.34), transparent 70%);
}

.ambient-b,
.orb-two {
    right: -60px;
    bottom: 12%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(73, 220, 177, 0.24), transparent 68%);
    animation-delay: -6s;
}

.ambient-c {
    top: 20%;
    right: 10%;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(255, 179, 71, 0.22), transparent 70%);
    animation-delay: -3s;
}

.page-shell {
    width: min(1220px, calc(100% - 32px));
    margin: 0 auto;
    padding: 28px 0 56px;
}

.topbar,
.hero-copy,
.hero-card,
.panel,
.stack-card,
.audit-row,
.log-card,
.login-card,
.login-sidekick,
.approval-card,
.user-badge {
    border: 1px solid var(--line);
    border-radius: 24px;
    background: var(--panel);
    backdrop-filter: blur(16px);
    box-shadow: var(--shadow);
}

.topbar,
.panel,
.hero-copy,
.hero-card,
.login-card,
.login-sidekick {
    position: relative;
    overflow: hidden;
}

.topbar::before,
.panel::before,
.hero-copy::before,
.hero-card::before,
.login-card::before,
.login-sidekick::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.06), transparent 45%, rgba(73, 220, 177, 0.07));
    pointer-events: none;
}

.topbar {
    padding: 18px 22px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    animation: rise 0.7s ease both;
}

.brand-title {
    font-size: 1.8rem;
    margin: 0;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.user-bar,
.panel-head.spread,
.log-head,
.actions,
.inline-actions,
.pager,
.form-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
}

.user-badge {
    padding: 12px 16px;
    min-width: 240px;
}

.user-badge p {
    color: var(--muted);
    font-size: 0.92rem;
}

.hero {
    display: grid;
    grid-template-columns: 2.2fr 1fr;
    gap: 20px;
    align-items: stretch;
    margin-bottom: 24px;
}

.hero.compact {
    grid-template-columns: 1fr;
}

.hero-copy,
.hero-card,
.panel,
.stack-card,
.audit-row,
.log-card,
.approval-card {
    animation: rise 0.8s ease both;
}

.panel:nth-of-type(2) {
    animation-delay: 0.08s;
}

.panel:nth-of-type(3) {
    animation-delay: 0.16s;
}

.panel:nth-of-type(4) {
    animation-delay: 0.24s;
}

.hero-copy {
    padding: 30px;
}

.cinematic {
    position: relative;
    overflow: hidden;
}

.cinematic::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, transparent 0%, rgba(255, 255, 255, 0.22) 48%, transparent 100%);
    transform: translateX(-120%);
    animation: sheen 7s ease-in-out infinite;
}

.hero-card {
    padding: 28px;
    display: grid;
    gap: 18px;
    align-content: center;
    background:
        radial-gradient(circle at top right, rgba(73, 220, 177, 0.2), transparent 32%),
        linear-gradient(180deg, rgba(14, 34, 49, 0.96), rgba(10, 24, 36, 0.94));
}

.floating-card {
    animation: rise 0.9s ease both, bob 5s ease-in-out infinite 1.1s, pulseGlow 4s ease-in-out infinite;
}

.hero-card span,
.kv-grid span,
label span,
.audit-row span,
.user-badge span,
.approval-banner span {
    display: block;
    margin-bottom: 6px;
    color: var(--muted);
    font-size: 0.8rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.hero-card strong,
.kv-grid strong {
    font-size: 1.55rem;
}

.eyebrow {
    margin: 0 0 10px;
    color: #ffd4c6;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

h1,
h2,
h3,
strong {
    margin: 0;
    font-weight: 700;
    color: var(--ink);
}

h1 {
    font-size: clamp(2.1rem, 5vw, 4rem);
    line-height: 0.98;
    max-width: 15ch;
}

h2 {
    font-size: 1.35rem;
    margin-bottom: 4px;
}

h3 {
    font-size: 1.05rem;
}

p {
    margin: 0;
    line-height: 1.6;
}

.hero-text {
    margin-top: 12px;
    max-width: 58ch;
    color: var(--muted);
}

.panel {
    padding: 22px;
    margin-bottom: 22px;
}

.highlight-panel {
    background:
        linear-gradient(135deg, rgba(255, 122, 89, 0.16), rgba(73, 220, 177, 0.14)),
        rgba(10, 26, 39, 0.86);
}

.panel-head {
    margin-bottom: 18px;
}

.grid {
    display: grid;
    gap: 22px;
    margin-bottom: 22px;
}

.grid.two-col {
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid.single {
    grid-template-columns: 1fr;
}

.approval-grid,
.stack-form,
.stack-list,
.audit-list,
.login-users {
    display: grid;
    gap: 14px;
}

.approval-card {
    padding: 18px;
    background:
        linear-gradient(135deg, rgba(255, 122, 89, 0.15), rgba(73, 220, 177, 0.12)),
        rgba(10, 28, 41, 0.88);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.approval-card:hover,
.stack-card:hover,
.audit-row:hover,
.log-card:hover,
.user-chip:hover {
    transform: translateY(-4px);
    border-color: rgba(73, 220, 177, 0.34);
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.compact-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.start-step-form {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--line);
}

.full {
    grid-column: 1 / -1;
}

label {
    display: block;
}

input,
textarea,
select {
    width: 100%;
    border: 1px solid rgba(154, 230, 225, 0.16);
    border-radius: 16px;
    padding: 12px 14px;
    font: inherit;
    color: var(--ink);
    background: rgba(9, 20, 31, 0.68);
    transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

input:focus,
textarea:focus,
select:focus {
    outline: none;
    border-color: rgba(73, 220, 177, 0.5);
    box-shadow: 0 0 0 4px rgba(73, 220, 177, 0.14);
    transform: translateY(-1px);
}

textarea,
pre {
    resize: vertical;
}

pre {
    margin: 0;
    padding: 16px;
    overflow: auto;
    border-radius: 18px;
    border: 1px solid var(--line);
    background: var(--panel-strong);
    color: var(--ink);
    font-size: 0.9rem;
}

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 44px;
    padding: 10px 18px;
    border: 0;
    border-radius: 999px;
    text-decoration: none;
    font: inherit;
    font-weight: 700;
    color: #fff9f3;
    background: linear-gradient(135deg, var(--accent), var(--accent-dark));
    cursor: pointer;
    transition: transform 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
    box-shadow: 0 12px 28px rgba(255, 79, 122, 0.24);
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 34px rgba(255, 79, 122, 0.34);
}

.btn.secondary {
    background: linear-gradient(135deg, #21425a, #286a6e);
    box-shadow: 0 10px 24px rgba(40, 106, 110, 0.22);
}

.btn.warning {
    background: linear-gradient(135deg, #ff9f43, var(--warning));
}

.btn.danger {
    background: linear-gradient(135deg, #ff6b81, var(--danger));
}

.btn.wide {
    width: 100%;
}

.btn.tiny {
    min-height: 36px;
    padding: 8px 14px;
    font-size: 0.9rem;
}

.subtle-link {
    color: #ffe5d5;
    text-decoration: none;
    font-weight: 700;
}

.search-bar {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.table-wrap {
    overflow: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 14px 12px;
    border-bottom: 1px solid var(--line);
    text-align: left;
    vertical-align: top;
}

th {
    color: var(--muted);
    font-size: 0.82rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.mono {
    font-family: "Courier New", monospace;
    font-size: 0.86rem;
}

.pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    color: #fffdf8;
    background: #375563;
    text-transform: capitalize;
}

.pill.active,
.pill.completed {
    background: var(--success);
}

.pill.inactive,
.pill.failed {
    background: var(--danger);
}

.pill.canceled,
.pill.warning {
    background: var(--warning);
}

.pill.neutral {
    background: #375563;
}

.stack-card,
.audit-row,
.log-card {
    padding: 16px 18px;
}

.audit-row {
    display: grid;
    grid-template-columns: 2fr repeat(2, 1fr) 1.3fr auto;
    gap: 12px;
    align-items: center;
}

.rule-section {
    padding: 18px 0;
    border-top: 1px solid var(--line);
}

.rule-section:first-of-type {
    padding-top: 0;
    border-top: 0;
}

.slim {
    margin-top: 12px;
}

.empty-state,
.error-text {
    color: var(--muted);
}

.error-text,
.error-banner {
    color: var(--danger);
}

.error-banner {
    padding: 12px 14px;
    border-radius: 14px;
    background: rgba(159, 42, 42, 0.08);
    border: 1px solid rgba(159, 42, 42, 0.18);
}

.kv-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 16px;
}

.empty-panel,
.approval-banner {
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 12px;
}

.empty-panel {
    border: 1px dashed rgba(154, 230, 225, 0.18);
    background: rgba(8, 22, 33, 0.74);
}

.approval-banner {
    border: 1px solid rgba(73, 220, 177, 0.22);
    background: linear-gradient(135deg, rgba(73, 220, 177, 0.16), rgba(255, 122, 89, 0.14));
    display: flex;
    justify-content: space-between;
    gap: 14px;
    align-items: center;
}

.login-shell {
    width: min(1080px, calc(100% - 32px));
    display: grid;
    grid-template-columns: 1.2fr 0.8fr;
    gap: 22px;
    align-items: stretch;
}

.login-card,
.login-sidekick {
    padding: 28px;
    animation: rise 0.8s ease both;
}

.user-chip {
    padding: 14px 16px;
    border: 1px solid var(--line);
    border-radius: 18px;
    background: rgba(12, 28, 41, 0.78);
}

@keyframes rise {
    from {
        opacity: 0;
        transform: translateY(18px) scale(0.985);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes bob {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-8px);
    }
}

@keyframes drift {
    0%, 100% {
        transform: translate3d(0, 0, 0) scale(1);
    }
    50% {
        transform: translate3d(18px, -16px, 0) scale(1.05);
    }
}

@keyframes sheen {
    0% {
        transform: translateX(-120%);
    }
    55%, 100% {
        transform: translateX(140%);
    }
}

@keyframes pulseGlow {
    0%, 100% {
        box-shadow: 0 18px 40px rgba(255, 79, 122, 0.18);
    }
    50% {
        box-shadow: 0 24px 52px rgba(73, 220, 177, 0.2);
    }
}

@media (max-width: 960px) {
    .hero,
    .grid.two-col,
    .audit-row,
    .compact-grid,
    .form-grid,
    .login-shell {
        grid-template-columns: 1fr;
    }

    .topbar,
    .approval-banner {
        align-items: flex-start;
    }

    .page-shell {
        width: min(100% - 20px, 1220px);
        padding: 20px 0 40px;
    }
}
"""
