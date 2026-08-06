import os
import re
import subprocess
import sys
import tempfile
import yaml

CONTENT_DIR = "content"
OUTPUT_DIR = "report/generated"
LUA_FILTER = os.path.join("scripts", "hugo-notice.lua")

SECTION_TITLES_VI = {
    "1-Worklog": "Nhật ký công việc",
    "2-Proposal": "Đề xuất",
    "3-BlogsPosted": "Các bài viết đã đăng",
    "4-EventParticipated": "Các sự kiện đã tham gia",
    "5-Workshop": "Hội thảo thực hành",
    "6-Self-evaluation": "Tự đánh giá",
    "7-Feedback": "Chia sẻ, đóng góp ý kiến",
}

SECTION_TITLES_EN = {
    "1-Worklog": "Worklog",
    "2-Proposal": "Proposal",
    "3-BlogsPosted": "Blogs Posted",
    "4-EventParticipated": "Events Participated",
    "5-Workshop": "Workshop",
    "6-Self-evaluation": "Self-Evaluation",
    "7-Feedback": "Sharing and Feedback",
}

CORE_REPORT_HEADINGS = {
    "2-Proposal": {
        "Project Summary", "Problem Statement", "Benefits and Value",
        "Architecture explanation", "Component responsibility table",
        "Design rationale", "AWS Services Used", "Component Design",
        "Implementation Phases", "Technical Requirements",
        "Timeline and Milestones", "Cost assumptions", "Cost Optimization",
        "Risk Matrix", "Mitigation Measures", "Expected Outcomes",
        "Tóm tắt dự án", "Giải pháp đề xuất", "Lợi ích và giá trị",
        "Giải thích kiến trúc", "Lý do thiết kế", "Kết quả dự kiến",
    },
    "5-Workshop/5.2-Architecture": {
        "Objective", "Scope", "Architecture context", "Component descriptions",
        "Public and private resources", "Security boundaries", "Expected result",
        "Outcome", "Mục tiêu", "Bối cảnh kiến trúc",
        "Mô tả các thành phần", "Ranh giới bảo mật", "Kết luận",
    },
    "5-Workshop/5.4-Source-Code-Preparation": {
        "Objective", "Architecture context", "Repository structure",
        "Review branch and workflow state", "Identify service dependencies",
        "Environment templates", "Deployment preparation",
        "GitHub Actions workflow modes", "Expected result", "Outcome",
        "Mục tiêu", "Cấu trúc repository",
        "Các chế độ của quy trình GitHub Actions", "Kết luận",
    },
    "5-Workshop/5.5-AWS-Infrastructure": {
        "Objective", "Scope", "Architecture context", "Implemented resources",
        "Network foundation", "IAM and OIDC", "ECR", "EKS cluster and workloads",
        "AWS Load Balancer Controller and ALB", "S3 and CloudFront",
        "Messaging and event-driven resources", "SageMaker resources",
        "Proposed hardening", "Expected result", "Outcome", "Mục tiêu",
        "Các tài nguyên đã được triển khai", "Kết luận",
    },
    "5-Workshop/5.6-Database-Deployment": {
        "Objective", "Architecture context", "PostgreSQL deployment",
        "Alembic migrations", "PostgreSQL connection configuration",
        "ElastiCache Redis", "DynamoDB chat tables",
        "DynamoDB Lambda dedupe table", "Data consistency design",
        "Expected result", "Outcome", "Mục tiêu", "Bối cảnh kiến trúc",
        "Thiết kế đảm bảo tính nhất quán dữ liệu", "Kết luận",
    },
    "5-Workshop/5.7-Backend-Deployment": {
        "Objective", "Architecture context", "Deployment inputs",
        "Image build and ECR push", "Kubernetes namespace and ServiceAccount",
        "ConfigMap and Secret usage", "Migration and chat initialization jobs",
        "Workload deployments", "AI and processing worker gate", "Health probes",
        "HPA and PDB", "Ingress and ALB routing", "Expected result", "Outcome",
        "Mục tiêu", "Bối cảnh kiến trúc", "Triển khai các workload", "Kết luận",
    },
    "5-Workshop/5.8-Frontend-Deployment": {
        "Objective", "Architecture context", "Vite environment configuration",
        "S3 publishing", "CloudFront configuration",
        "GitHub Actions frontend deployment", "Verification", "Expected result",
        "Outcome", "Mục tiêu",
        "Bối cảnh kiến trúc", "Kết luận",
    },
    "5-Workshop/5.9-Monitoring-and-Logging": {
        "Objective", "Architecture context", "Kubernetes resource inspection",
        "Rollout status", "Application logs", "Health endpoints",
        "Prometheus and Grafana", "Repository-defined alerts", "CloudWatch Logs",
        "AWS managed-service metrics", "Proposed CloudWatch alarms",
        "Expected result", "Outcome", "Mục tiêu",
        "Bối cảnh kiến trúc", "Kết luận",
    },
    "5-Workshop/5.10-End-to-End-Testing": {
        "Objective", "Architecture context", "Test status definitions",
        "Acceptance test table", "Database result checks", "Storage result checks",
        "CloudWatch log checks", "Expected result", "Outcome", "Mục tiêu",
        "Bảng kiểm thử nghiệm thu (Acceptance test table)", "Kết luận",
    },
    "5-Workshop/5.11-Security-and-Cost": {
        "Objective", "Architecture context", "Security controls",
        "Authentication and authorization", "Data protection",
        "Observed Week 8 service cost", "Cost assumptions", "Cost estimation table",
        "Largest cost drivers", "Cost optimization options", "Expected result", "Outcome",
        "Mục tiêu", "Các biện pháp kiểm soát bảo mật",
        "Chi phí thực tế các dịch vụ trong Tuần 8", "Kết luận",
    },
    "5-Workshop/5.12-Troubleshooting": {
        "Objective", "Architecture context", "Troubleshooting table",
        "Detailed incident notes", "General diagnostic workflow", "Expected result", "Outcome",
        "Mục tiêu", "Bảng xử lý sự cố (Troubleshooting table)",
        "Quy trình chẩn đoán tổng quát (General diagnostic workflow)", "Kết luận",
    },
}

MERMAID_FLOW_DESCRIPTIONS = {
    "en": {
        ("1-Worklog/1.1-Week1", 1): (
            "The browser uses the React/Vite frontend, which calls the FastAPI backend "
            "for application functions and the Socket.IO service for realtime chat. The "
            "backend relies on PostgreSQL, document storage, and the AI service, while chat "
            "uses Redis pub/sub and DynamoDB tables."
        ),
        ("1-Worklog/1.2-Week2", 1): (
            "A client submits an application with an idempotency key. The backend reserves "
            "the key in PostgreSQL, creates the application for a new request, returns the "
            "stored response for an exact replay, and returns HTTP 409 when the payload or "
            "business state conflicts."
        ),
        ("1-Worklog/1.3-Week3", 1): (
            "The backend commits the business change and an outbox row in PostgreSQL. The "
            "dispatcher claims pending events and publishes them to SQS; successful events "
            "are marked published, temporary failures are retried with backoff, and terminal "
            "failures are marked dead. Consumers deduplicate messages by event ID."
        ),
        ("1-Worklog/1.5-Week5", 1): (
            "The local kind cluster contains the application workloads and local data "
            "services in the internship namespace. A separate monitoring namespace runs "
            "Prometheus, Grafana, Loki, and Tempo; Prometheus collects metrics from the "
            "backend, chat service, and outbox dispatcher."
        ),
        ("1-Worklog/1.6-Week6", 1): (
            "GitHub Actions obtains an OIDC token and assumes the scoped deployment role. "
            "That role permits SHA-tagged backend and chat images to be pushed to ECR and "
            "allows the deployment script to update the EKS workloads without long-lived "
            "AWS credentials."
        ),
        ("1-Worklog/1.7-Week7", 1): (
            "CloudFront forwards application traffic through the public ALB to the backend "
            "and chat services. The backend uses RDS, S3, and the SQS outbox queue; chat uses "
            "ElastiCache and DynamoDB; the processing worker calls the AI service and "
            "SageMaker, while the dispatcher publishes events to SQS."
        ),
        ("1-Worklog/1.8-Week8", 1): (
            "The production entry point is CloudFront: static frontend requests go to S3, "
            "while API and chat paths go through the ALB to EKS. Application data flows to "
            "RDS, Redis, and DynamoDB; asynchronous CV processing uses the worker, AI service, "
            "and SageMaker; outbox events reach SQS and the notification Lambda."
        ),
        ("2-Proposal", 1): (
            "CloudFront serves the private S3 frontend and routes API, chat, and Socket.IO "
            "traffic to the ALB. EKS hosts the backend, chat, dispatcher, worker, and AI "
            "services, which use RDS, Redis, DynamoDB, S3, SQS, Lambda, SES, and SageMaker. "
            "GitHub Actions deploys images, workloads, frontend assets, and CloudFront changes "
            "through OIDC-based AWS access."
        ),
        ("5-Workshop/5.2-Architecture", 1): (
            "Users enter through CloudFront, which serves the private S3 frontend or forwards "
            "dynamic requests to the ALB and EKS. EKS workloads connect to RDS, DynamoDB, "
            "Redis, S3, SageMaker, and the SQS/Lambda notification path, with a DLQ and "
            "DynamoDB deduplication table for resilient event handling."
        ),
        ("5-Workshop/5.2-Architecture", 2): (
            "CloudFront evaluates each HTTPS path. The default behavior serves the S3 "
            "frontend; `/api/*` is forwarded to the backend service; `/chat/*` and "
            "`/socket.io/*` are forwarded to the chat service through the ALB."
        ),
        ("5-Workshop/5.2-Architecture", 3): (
            "A candidate submits a CV through the frontend, and the backend stores the "
            "document reference plus application, idempotency, outbox, and processing records. "
            "The worker claims the queued job, calls the AI adapter and SageMaker, saves the "
            "normalized result in PostgreSQL, and exposes the result for frontend polling."
        ),
        ("5-Workshop/5.2-Architecture", 4): (
            "Socket.IO traffic passes from CloudFront and the ALB to a chat-service pod. The "
            "receiving pod persists the message in DynamoDB, publishes the room event through "
            "Redis so other pods can notify subscribed users, and acknowledges the sender only "
            "after persistence."
        ),
        ("5-Workshop/5.2-Architecture", 5): (
            "The backend writes the business mutation and outbox event in one PostgreSQL "
            "transaction. The dispatcher publishes the event to SQS, after which Lambda uses "
            "a conditional DynamoDB write for deduplication; first-time events are archived in "
            "S3 and may trigger SES, while duplicates are treated as already processed."
        ),
        ("5-Workshop/5.2-Architecture", 6): (
            "A manually triggered GitHub Actions workflow validates the repository and restores "
            "compute when required, then builds SHA-tagged ECR images. It deploys the EKS "
            "application and public ALB, ensures the private S3/CloudFront configuration, "
            "publishes the frontend, invalidates CloudFront, and produces a deployment summary."
        ),
    },
    "vi": {
        ("1-Worklog/1.1-Week1", 1): (
            "Trình duyệt sử dụng frontend React/Vite; frontend gọi backend FastAPI cho các "
            "chức năng ứng tuyển và dịch vụ Socket.IO cho trò chuyện thời gian thực. Backend "
            "dùng PostgreSQL, kho tài liệu và dịch vụ AI, còn chat dùng Redis pub/sub và các "
            "bảng DynamoDB."
        ),
        ("1-Worklog/1.2-Week2", 1): (
            "Client gửi yêu cầu ứng tuyển kèm khóa idempotency. Backend giữ chỗ khóa trong "
            "PostgreSQL, tạo hồ sơ đối với yêu cầu mới, trả lại kết quả đã lưu khi yêu cầu được "
            "gửi lại y hệt, và trả HTTP 409 khi payload hoặc trạng thái nghiệp vụ xung đột."
        ),
        ("1-Worklog/1.3-Week3", 1): (
            "Backend ghi thay đổi nghiệp vụ và bản ghi outbox trong cùng PostgreSQL. Dispatcher "
            "lấy các sự kiện đang chờ và gửi sang SQS; sự kiện thành công được đánh dấu đã gửi, "
            "lỗi tạm thời được thử lại có backoff, còn lỗi cuối cùng được đánh dấu DEAD. Consumer "
            "khử trùng lặp theo mã sự kiện."
        ),
        ("1-Worklog/1.5-Week5", 1): (
            "Cụm kind cục bộ chứa các workload ứng dụng và dịch vụ dữ liệu trong namespace "
            "internship. Namespace monitoring riêng chạy Prometheus, Grafana, Loki và Tempo; "
            "Prometheus thu thập metric từ backend, chat service và outbox dispatcher."
        ),
        ("1-Worklog/1.6-Week6", 1): (
            "GitHub Actions nhận token OIDC và đảm nhận deployment role có phạm vi giới hạn. "
            "Role này cho phép đẩy image backend và chat gắn thẻ SHA lên ECR, đồng thời cho phép "
            "script triển khai cập nhật workload EKS mà không cần lưu AWS credential dài hạn."
        ),
        ("1-Worklog/1.7-Week7", 1): (
            "CloudFront chuyển lưu lượng ứng dụng qua ALB công khai đến backend và chat service. "
            "Backend dùng RDS, S3 và hàng đợi outbox SQS; chat dùng ElastiCache và DynamoDB; "
            "processing worker gọi AI service và SageMaker, còn dispatcher gửi sự kiện vào SQS."
        ),
        ("1-Worklog/1.8-Week8", 1): (
            "Điểm vào production là CloudFront: yêu cầu frontend tĩnh đi đến S3, còn API và chat "
            "đi qua ALB đến EKS. Dữ liệu ứng dụng được lưu tại RDS, Redis và DynamoDB; xử lý CV "
            "bất đồng bộ dùng worker, AI service và SageMaker; sự kiện outbox đi đến SQS và "
            "Lambda thông báo."
        ),
        ("2-Proposal", 1): (
            "CloudFront phục vụ frontend từ S3 riêng tư và chuyển lưu lượng API, chat, Socket.IO "
            "đến ALB. EKS chạy backend, chat, dispatcher, worker và AI service, kết nối với RDS, "
            "Redis, DynamoDB, S3, SQS, Lambda, SES và SageMaker. GitHub Actions triển khai image, "
            "workload, frontend và cấu hình CloudFront thông qua quyền AWS dựa trên OIDC."
        ),
        ("5-Workshop/5.2-Architecture", 1): (
            "Người dùng truy cập qua CloudFront; CloudFront phục vụ frontend S3 riêng tư hoặc "
            "chuyển yêu cầu động đến ALB và EKS. Các workload EKS kết nối RDS, DynamoDB, Redis, "
            "S3, SageMaker và tuyến thông báo SQS/Lambda; DLQ cùng bảng DynamoDB dedupe hỗ trợ xử "
            "lý sự kiện tin cậy."
        ),
        ("5-Workshop/5.2-Architecture", 2): (
            "CloudFront kiểm tra đường dẫn của từng yêu cầu HTTPS. Luồng mặc định phục vụ "
            "frontend từ S3; `/api/*` chuyển đến backend service; `/chat/*` và `/socket.io/*` "
            "chuyển đến chat service thông qua ALB."
        ),
        ("5-Workshop/5.2-Architecture", 3): (
            "Ứng viên nộp CV qua frontend; backend lưu tham chiếu tài liệu cùng các bản ghi ứng "
            "tuyển, idempotency, outbox và processing. Worker nhận job đang chờ, gọi AI adapter "
            "và SageMaker, lưu kết quả chuẩn hóa vào PostgreSQL, sau đó frontend truy vấn trạng "
            "thái để nhận kết quả."
        ),
        ("5-Workshop/5.2-Architecture", 4): (
            "Lưu lượng Socket.IO đi qua CloudFront và ALB đến một pod chat-service. Pod nhận tin "
            "nhắn sẽ lưu vào DynamoDB, phát sự kiện phòng qua Redis để các pod khác thông báo cho "
            "người dùng đang theo dõi, rồi mới gửi xác nhận cho người gửi."
        ),
        ("5-Workshop/5.2-Architecture", 5): (
            "Backend ghi thay đổi nghiệp vụ và sự kiện outbox trong một transaction PostgreSQL. "
            "Dispatcher gửi sự kiện vào SQS; Lambda dùng conditional write trên DynamoDB để khử "
            "trùng lặp. Sự kiện lần đầu được lưu trữ ở S3 và có thể gửi email qua SES, còn sự "
            "kiện trùng được xem là đã xử lý."
        ),
        ("5-Workshop/5.2-Architecture", 6): (
            "Workflow GitHub Actions được kích hoạt thủ công để kiểm tra repository và khôi phục "
            "compute khi cần, sau đó build image ECR gắn thẻ SHA. Pipeline triển khai ứng dụng "
            "EKS và ALB, bảo đảm cấu hình S3/CloudFront riêng tư, xuất bản frontend, tạo "
            "CloudFront invalidation và tổng hợp kết quả triển khai."
        ),
    },
}

WORKLOG_CORE_HEADINGS = {
    "Objectives", "Technical Implementation", "Problems and Solutions",
    "Testing, Build and Deployment Results", "Weekly Results", "Lessons Learned",
    "Mục tiêu", "Triển khai kỹ thuật", "Vấn đề và giải pháp",
    "Kết quả kiểm thử, build và triển khai", "Kết quả trong tuần", "Bài học kinh nghiệm",
}

LATEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

LATEX_TEXT_FALLBACKS = {
    "─": "-",
    "│": "|",
    "├": "+",
    "└": "+",
    "┐": "+",
    "┘": "+",
    "▼": "v",
    "►": ">",
    "↓": "v",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_dependencies():
    if not os.path.isdir(CONTENT_DIR):
        raise RuntimeError(f"Content directory not found: {CONTENT_DIR}")

    if not os.path.exists(LUA_FILTER):
        raise RuntimeError(f"Lua filter not found: {LUA_FILTER}")

    try:
        subprocess.run(
            ["pandoc", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError("pandoc is not installed or not in PATH")


def sort_key(dirpath):
    parts = []

    for seg in dirpath.split(os.sep):
        m = re.match(r"(\d+(?:\.\d+)*)", seg)
        if m:
            parts.append(tuple(int(x) for x in m.group(1).split(".")))
        else:
            parts.append((9999,))

    return tuple(parts)


def tex_safe(name):
    return re.sub(r"[^a-zA-Z0-9]", "_", name).strip("_")


def sanitize_latex_text(text):
    if text is None:
        return ""

    text = str(text)
    return re.sub(
        r"[\\&%$#_{}~^]",
        lambda m: LATEX_SPECIALS[m.group(0)],
        text,
    )


def extract_frontmatter(content):
    content = content.lstrip("\ufeff")
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", content, re.DOTALL)
    if not match:
        return {}

    try:
        fm = yaml.safe_load(match.group(1))
        return fm if isinstance(fm, dict) else {}
    except yaml.YAMLError:
        return {}


def read_frontmatter(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return extract_frontmatter(fh.read())
    except Exception as e:
        print(f"Warning: cannot read frontmatter from {path}: {e}", file=sys.stderr)
        return {}


def strip_frontmatter(content):
    content = content.lstrip("\ufeff").strip()
    match = re.match(r"^---\s*\n.*?\n---\s*(?:\n|$)", content, re.DOTALL)
    if match:
        return content[match.end():].strip()
    return content


def get_bool_meta(meta, keys, default):
    for key in keys:
        if key in meta:
            return bool(meta[key])
    return default


def get_list_meta(meta, keys):
    for key in keys:
        value = meta.get(key)
        if value is None:
            continue

        if isinstance(value, list):
            return [str(x) for x in value]

        if isinstance(value, str):
            return [x.strip() for x in value.split(",") if x.strip()]

    return []


def check_duplicate_outputs(pages):
    seen = {}

    for rel_dir, out_name, _title, _meta in pages:
        if out_name in seen:
            raise ValueError(
                f"Duplicate generated filename: {out_name}.tex\n"
                f"  - {seen[out_name]}\n"
                f"  - {rel_dir}"
            )

        seen[out_name] = rel_dir


# ---------------------------------------------------------------------------
# Markdown filters before Pandoc
# ---------------------------------------------------------------------------

def split_markdown_table_row(line):
    stripped = line.strip()

    if not stripped.startswith("|"):
        return None

    if stripped.endswith("|"):
        stripped = stripped[1:-1]
    else:
        stripped = stripped[1:]

    return [cell.strip() for cell in stripped.split("|")]


def is_markdown_table_separator(line):
    cells = split_markdown_table_row(line)
    if not cells:
        return False

    return all(re.match(r"^:?-{3,}:?$", cell.strip()) for cell in cells)


def make_markdown_table_row(cells):
    return "| " + " | ".join(cells) + " |"


def filter_markdown_tables(content, keep_columns):
    """Whitelist columns in Markdown pipe tables."""
    if not keep_columns:
        return content

    keep_norm = {c.strip().lower() for c in keep_columns}

    lines = content.splitlines()
    out = []
    i = 0

    while i < len(lines):
        is_table_start = (
            i + 1 < len(lines)
            and split_markdown_table_row(lines[i]) is not None
            and is_markdown_table_separator(lines[i + 1])
        )

        if not is_table_start:
            out.append(lines[i])
            i += 1
            continue

        header_cells = split_markdown_table_row(lines[i])
        sep_cells = split_markdown_table_row(lines[i + 1])

        keep_idx = [
            idx for idx, name in enumerate(header_cells)
            if name.strip().lower() in keep_norm
        ]

        if not keep_idx:
            out.append(lines[i])
            i += 1
            continue

        out.append(make_markdown_table_row([header_cells[idx] for idx in keep_idx]))
        out.append(make_markdown_table_row([sep_cells[idx] for idx in keep_idx]))

        i += 2

        while i < len(lines) and split_markdown_table_row(lines[i]) is not None:
            row_cells = split_markdown_table_row(lines[i])

            if len(row_cells) < len(header_cells):
                row_cells += [""] * (len(header_cells) - len(row_cells))

            out.append(make_markdown_table_row([row_cells[idx] for idx in keep_idx]))
            i += 1

    return "\n".join(out)

def normalize_col_name(name):
    return re.sub(r"\s+", " ", str(name).strip()).lower()


def latex_escape_cell(text):
    """Escape normal text for LaTeX table cells, but keep simple formatting."""
    if text is None:
        return ""

    text = str(text).strip()

    # Remove markdown links <https://...> -> https://...
    text = re.sub(r"<(https?://[^>]+)>", r"\1", text)

    # Markdown bold
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)

    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    # Escape only outside simple LaTeX commands introduced above.
    # Simpler and okay for report use:
    for k, v in replacements.items():
        if k == "\\":
            continue
        text = text.replace(k, v)

    # Restore \textbf after escaping braces.
    text = text.replace(r"\textbf\{", r"\textbf{").replace(r"\}", "}")

    return text


def task_cell_to_latex(text):
    """Convert a worklog Task cell with <br>, '-' and '+' markers to multiline LaTeX."""
    if not text:
        return ""

    text = str(text)

    # Normalize line breaks from Hugo/Markdown table cell.
    text = text.replace("<br>", "\n")
    text = text.replace("<br/>", "\n")
    text = text.replace("<br />", "\n")
    text = text.replace("&emsp;", " ")

    raw_lines = [x.strip() for x in text.splitlines()]
    raw_lines = [x for x in raw_lines if x]

    if not raw_lines:
        return ""

    out = []
    in_itemize = False

    def open_itemize():
        nonlocal in_itemize
        if not in_itemize:
            out.append(r"\begin{itemize}")
            out.append(r"\setlength\itemsep{0.15em}")
            out.append(r"\setlength\parskip{0pt}")
            in_itemize = True

    def close_itemize():
        nonlocal in_itemize
        if in_itemize:
            out.append(r"\end{itemize}")
            in_itemize = False

    for line in raw_lines:
        line = line.strip()

        # "- Task"
        if line.startswith("-"):
            open_itemize()
            item = line[1:].strip()
            out.append(r"\item " + latex_escape_cell(item))

        # "+ sub task"
        elif line.startswith("+"):
            open_itemize()
            item = line[1:].strip()
            out.append(r"\item[] \hspace{1em}+ " + latex_escape_cell(item))

        # fallback normal line
        else:
            if in_itemize:
                out.append(r"\item " + latex_escape_cell(line))
            else:
                out.append(latex_escape_cell(line) + r"\\")

    close_itemize()

    return "\n".join(out)


def simple_cell_to_latex(text):
    """Convert normal table cell to LaTeX."""
    if text is None:
        return ""

    text = str(text).strip()
    text = text.replace("<br>", r"\\ ")
    text = text.replace("<br/>", r"\\ ")
    text = text.replace("<br />", r"\\ ")
    text = text.replace("&emsp;", " ")

    return latex_escape_cell(text)


def extract_first_markdown_table(content):
    """Extract first pipe markdown table.

    Returns: before, header_cells, rows, after
    """
    lines = content.splitlines()

    for i in range(len(lines) - 1):
        if (
            split_markdown_table_row(lines[i]) is not None
            and is_markdown_table_separator(lines[i + 1])
        ):
            header = split_markdown_table_row(lines[i])
            rows = []

            j = i + 2
            while j < len(lines) and split_markdown_table_row(lines[j]) is not None:
                row = split_markdown_table_row(lines[j])

                if len(row) < len(header):
                    row += [""] * (len(header) - len(row))

                rows.append(row[:len(header)])
                j += 1

            before = "\n".join(lines[:i]).strip()
            after = "\n".join(lines[j:]).strip()

            return before, header, rows, after

    return content, None, None, ""


def render_worklog_table_latex(header, rows, keep_columns):
    """Render worklog markdown table as custom LaTeX longtable."""
    header_norm = [normalize_col_name(h) for h in header]
    keep_norm = [normalize_col_name(c) for c in keep_columns]

    keep_idx = []
    keep_names = []

    for col in keep_norm:
        if col in header_norm:
            idx = header_norm.index(col)
            keep_idx.append(idx)
            keep_names.append(header[idx])

    if not keep_idx:
        keep_idx = list(range(len(header)))
        keep_names = header

    # Detect columns
    day_names = {"day", "thứ", "thu"}
    task_names = {"task", "công việc", "cong viec"}
    complete_names = {"completion date", "complete date", "ngày hoàn thành", "ngay hoan thanh"}

    latex = []
    latex.append(r"\begingroup")
    latex.append(r"\small")
    latex.append(r"\setlength{\tabcolsep}{5pt}")
    latex.append(r"\renewcommand{\arraystretch}{1.2}")
    latex.append(r"\begin{longtable}{@{}p{0.07\linewidth}p{0.72\linewidth}p{0.17\linewidth}@{}}")
    latex.append(r"\toprule")

    # Force nicer names based on selected columns count.
    display_headers = []
    for name in keep_names:
        n = normalize_col_name(name)
        if n in day_names:
            display_headers.append("Day" if name.lower() == "day" else "Thứ")
        elif n in task_names:
            display_headers.append("Task" if name.lower() == "task" else "Công việc")
        elif n in complete_names:
            display_headers.append("Completion Date" if "date" in name.lower() else "Ngày hoàn thành")
        else:
            display_headers.append(name)

    # If user selects exactly Day/Task/Completion, use 3-column layout.
    latex.append(" & ".join(r"\textbf{" + latex_escape_cell(h) + "}" for h in display_headers) + r" \\")
    latex.append(r"\midrule")
    latex.append(r"\endhead")
    latex.append(r"\bottomrule")
    latex.append(r"\endfoot")

    for row in rows:
        selected = [row[idx] if idx < len(row) else "" for idx in keep_idx]
        rendered = []

        for name, cell in zip(keep_names, selected):
            n = normalize_col_name(name)

            if n in task_names:
                rendered.append(task_cell_to_latex(cell))
            else:
                rendered.append(simple_cell_to_latex(cell))

        latex.append(" & ".join(rendered) + r" \\")
        latex.append(r"\addlinespace[0.35em]")

    latex.append(r"\end{longtable}")
    latex.append(r"\endgroup")

    return "\n".join(latex)


def preprocess_worklog_markdown(content, meta, compact=True):
    """Convert worklog markdown table into raw LaTeX before Pandoc."""
    content = strip_frontmatter(content)

    keep_columns = get_list_meta(
        meta,
        ["reportTableColumns", "report_table_columns", "latexTableColumns", "latex_table_columns"],
    )

    before, header, rows, after = extract_first_markdown_table(content)

    if header is None:
        return content

    table_latex = render_worklog_table_latex(header, rows, keep_columns)

    pieces = []
    if before:
        pieces.append(before)

    pieces.append(table_latex)

    if after and not compact:
        pieces.append(after)

    return "\n\n".join(pieces)

def filter_markdown_sections(content, keep_headings):
    """Whitelist markdown sections by heading text.

    Keeps content before the first heading.
    If a heading is kept, its subsection content is kept until another
    same-level or higher-level heading appears.
    """
    if not keep_headings:
        return content

    keep_norm = {h.strip().lower() for h in keep_headings}

    lines = content.splitlines()
    out = []

    keep_stack_level = None
    before_first_heading = True
    keeping = True

    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)

        if m:
            before_first_heading = False
            level = len(m.group(1))
            title = re.sub(r"\s+#*$", "", m.group(2)).strip()
            title_norm = title.lower()

            if title_norm in keep_norm:
                keeping = True
                keep_stack_level = level
                out.append(line)
                continue

            if keep_stack_level is not None and level > keep_stack_level and keeping:
                out.append(line)
                continue

            keeping = False
            keep_stack_level = None
            continue

        if before_first_heading or keeping:
            out.append(line)

    return "\n".join(out)


def compact_report_markdown(content, lang, rel_dir=None):
    """Normalize Hugo-only markup without removing deployed web content."""

    normalized_rel = (rel_dir or "").replace("\\", "/")
    diagram_index = 0

    # Mermaid is rendered to vector PDF by scripts/render_mermaid.js. Embed the
    # generated asset here so graph/flow definitions never appear as source code
    # in the report.
    def replace_mermaid(match):
        nonlocal diagram_index
        diagram_index += 1
        heading_marks = match.group(1)
        heading_title = match.group(2)
        heading_prefix = ""
        if heading_marks and heading_title:
            heading_prefix = f"{heading_marks} {heading_title}\n\n"

        description = MERMAID_FLOW_DESCRIPTIONS.get(lang, {}).get(
            (normalized_rel, diagram_index)
        )
        if not description:
            description = (
                "This flow summarizes the main actors, processing steps, and "
                "service dependencies."
                if lang == "en"
                else "Luồng này tóm tắt các tác nhân, bước xử lý và quan hệ phụ thuộc dịch vụ chính."
            )
        label = "Flow summary." if lang == "en" else "Mô tả sơ bộ."
        return (
            "\n\n"
            + heading_prefix
            + f"**{label}** {description}\n\n"
        )

    content = re.sub(
        r"(?:(?:^(#{1,6})[ \t]+([^\n]+)\s*$)\s*)?"
        r"\{\{<\s*mermaid(?:\s+[^>]*)?\s*>\}\}\s*([\s\S]*?)\s*\{\{<\s*/mermaid\s*>\}\}",
        replace_mermaid,
        content,
        flags=re.MULTILINE,
    )

    # Internal links in heading text make Pandoc emit deeply nested heading
    # macros that conflict with the report's heading-neutralization pass. The
    # PDF needs the label only; navigation remains available in the web report.
    content = re.sub(
        r"^(#{1,6}\s+)\[([^\]]+)\]\([^)]+\)\s*$",
        r"\1\2",
        content,
        flags=re.MULTILINE,
    )

    return re.sub(r"\n{3,}", "\n\n", content)


def preprocess_markdown(content, meta=None, lang="en", rel_dir=None):
    content = strip_frontmatter(content)

    normalized_rel = (rel_dir or "").replace("\\", "/")
    if normalized_rel.startswith("4-EventParticipated"):
        # Keep the event write-up, but omit personal evidence photos from the
        # generated report as requested.
        content = re.sub(
            r"^[ \t]*!\[[^\]]*\]\([^\n)]*3-Events/Evidence_Events[^\n)]*\)[ \t]*$",
            "",
            content,
            flags=re.IGNORECASE | re.MULTILINE,
        )

    content = compact_report_markdown(content, lang, rel_dir=rel_dir)

    content = re.sub(r"!\[([^\]]*)\]\(/static/images/", r"![\1](", content)
    content = re.sub(r"!\[([^\]]*)\]\(/images/",      r"![\1](", content)
    content = re.sub(r"!\[([^\]]*)\]\(/static/logs/", r"![\1](../static/logs/", content)
    content = re.sub(r"!\[([^\]]*)\]\(/logs/",        r"![\1](../static/logs/", content)

    content = re.sub(
        r"\{\{%\s*notice\s+(\w+)\s*%\}\}\s*",
        r"\n::: {\1}\n",
        content,
    )
    content = re.sub(r"\s*\{\{%\s*/notice\s*%\}\}", r"\n:::\n", content)

    content = content.replace("&emsp;", r"\qquad ")
    content = content.replace("\u2705", r"\checkmark")
    content = content.replace("\u2610", r"$\square$")
    content = re.sub(r"⚠\ufe0f?", "!", content)
    content = content.replace("\u26a0", "!")
    content = content.replace("\u2192", r"$\rightarrow$")

    for original, replacement in LATEX_TEXT_FALLBACKS.items():
        content = content.replace(original, replacement)

    return content
# ---------------------------------------------------------------------------
# Pandoc LaTeX conversion
# ---------------------------------------------------------------------------
def neutralize_body_headings(latex):
    """Convert Pandoc headings to visual bold headings."""

    heading_cmds = ["section", "subsection", "subsubsection", "paragraph", "subparagraph"]

    # 1. Bỏ toàn bộ \hypertarget wrapper nhưng giữ nội dung bên trong.
    # Pandoc thường sinh:
    # \hypertarget{id}{%
    # \section{Title}\label{id}}
    latex = re.sub(
        r"\\hypertarget\{[^{}]*\}\{\s*%?\s*",
        "",
        latex,
        flags=re.DOTALL,
    )

    # Sau khi bỏ phần mở \hypertarget, thường sẽ dư "}" sau \label hoặc sau heading.
    latex = re.sub(
        r"(\\label\{[^{}]*\})\s*\}",
        r"\1",
        latex,
        flags=re.DOTALL,
    )

    # 2. Remove labels.
    latex = re.sub(r"\\label\{[^{}]*\}", "", latex)

    # 3. Convert standalone headings thành text đậm.
    for cmd in heading_cmds:
        latex = re.sub(
            rf"\\{cmd}\{{([^{{}}]*)\}}",
            r"\\vspace{0.5em}\\noindent\\textbf{\1}\\par",
            latex,
            flags=re.DOTALL,
        )

    # 4. Safety net: nếu vẫn còn dạng hỏng:
    # \hypertarget{id}{\vspace{0.5em}\noindent\textbf{Title}\par}
    latex = re.sub(
        r"\\hypertarget\{[^{}]*\}\{\s*(\\vspace\{0\.5em\}\\noindent\\textbf\{[^{}]*\}\\par)\s*\}",
        r"\1",
        latex,
        flags=re.DOTALL,
    )
    latex = re.sub(
        r"(\\vspace\{0\.5em\}\\noindent\\textbf\{[^{}]*\}\\par)\}",
        r"\1",
        latex,
        flags=re.DOTALL,
    )

    return latex

def compact_longtables(latex):
    """Make Pandoc longtables more compact without modifying column specs."""
    if r"\begin{longtable}" not in latex:
        return latex

    latex = latex.replace(
        r"\begin{longtable}",
        r"""\begingroup
\small
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.15}
\begin{longtable}"""
    )

    latex = latex.replace(
        r"\end{longtable}",
        r"""\end{longtable}
\endgroup"""
    )

    return latex


def add_texttt_breakpoints(latex):
    """Allow long inline monospace identifiers to wrap inside table cells."""
    marker = r"\texttt{"
    output = []
    cursor = 0

    while True:
        start = latex.find(marker, cursor)
        if start < 0:
            output.append(latex[cursor:])
            break

        output.append(latex[cursor:start])
        content_start = start + len(marker)
        depth = 1
        index = content_start

        while index < len(latex) and depth:
            if latex[index] == "{":
                depth += 1
            elif latex[index] == "}":
                depth -= 1
            index += 1

        if depth:
            output.append(latex[start:])
            break

        content = latex[content_start:index - 1]
        if r"\allowbreak{}" not in content:
            content = re.sub(
                r"(?<=[A-Za-z0-9])-(?=[A-Za-z0-9])",
                r"-\\allowbreak{}",
                content,
            )
            content = content.replace(r"\_", r"\_\allowbreak{}")
            content = content.replace("/", r"/\allowbreak{}")
            content = content.replace(".", r".\allowbreak{}")

        output.append(marker + content + "}")
        cursor = index

    return "".join(output)


def postprocess_latex(latex):
    # Do NOT replace Pandoc table column specs by regex.
    latex = re.sub(r"\\label\{[^}]+\}", "", latex)
    latex = re.sub(
        r"\{\s*\\def\\LTcaptype\{none\}\s*%[^\n]*\n",
        "{\n",
        latex,
    )
    latex = latex.replace(r"\begin{longtable}[]{", r"\begin{longtable}{")
    latex = add_texttt_breakpoints(latex)
    latex = neutralize_body_headings(latex)
    latex = compact_longtables(latex)
    return latex


def convert_to_latex(md_text, source_path=None):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_in = os.path.join(tmpdir, "input.md")
        tmp_out = os.path.join(tmpdir, "output.tex")

        with open(tmp_in, "w", encoding="utf-8") as f:
            f.write(md_text)

        try:
            subprocess.run(
                [
                    "pandoc",
                    tmp_in,
                    "-f", "markdown+raw_tex+fenced_divs+bracketed_spans",
                    "-t", "latex",
                    "--top-level-division=section",
                    "--lua-filter", LUA_FILTER,
                    "-o", tmp_out,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            if source_path:
                print(f"\nPandoc failed for: {source_path}", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
            raise

        with open(tmp_out, encoding="utf-8") as f:
            latex = f.read()

    return postprocess_latex(latex)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover_pages(lang):
    suffix = ".vi" if lang == "vi" else ""
    filename = f"_index{suffix}.md"

    all_dirs = set()
    pages = []
    skip_dirs = set()

    for root, _dirs, files in os.walk(CONTENT_DIR):
        rel = os.path.relpath(root, CONTENT_DIR)

        if rel == ".":
            continue

        # If any ancestor directory is skipped, skip this directory too.
        if any(rel == d or rel.startswith(d + os.sep) for d in skip_dirs):
            continue

        if filename not in files:
            continue

        md_path = os.path.join(root, filename)
        meta = read_frontmatter(md_path)

        include = get_bool_meta(
            meta,
            ["includeInReport", "include_in_report", "isincludeinlatex", "includeInLatex"],
            True,
        )

        if not include:
            print(f"  SKIP: {rel}")
            skip_dirs.add(rel)
            continue

        if get_bool_meta(meta, ["draft"], False):
            print(f"  SKIP DRAFT: {rel}")
            skip_dirs.add(rel)
            continue

        all_dirs.add(rel)

        title = meta.get("title")
        title = str(title) if title is not None else None

        pages.append((rel, tex_safe(rel), title, meta))

    container_dirs = {
        d for d in all_dirs
        if any(p.startswith(d + os.sep) for p in all_dirs)
    }

    pages.sort(key=lambda p: sort_key(p[0]))
    check_duplicate_outputs(pages)

    return pages, container_dirs
# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------

def process_language(lang):
    suffix = ".vi" if lang == "vi" else ""
    lang_dir = os.path.join(OUTPUT_DIR, lang)
    os.makedirs(lang_dir, exist_ok=True)

    pages, containers = discover_pages(lang)

    for rel_dir, out_name, _title, meta in pages:
        md_path = os.path.join(CONTENT_DIR, rel_dir, f"_index{suffix}.md")

        with open(md_path, encoding="utf-8") as f:
            md_content = f.read()

        processed = preprocess_markdown(
            md_content,
            meta=meta,
            lang=lang,
            rel_dir=rel_dir,
        )
        latex = convert_to_latex(processed, source_path=md_path)

        out_path = os.path.join(lang_dir, f"{out_name}.tex")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(latex)

        marker = "C" if rel_dir in containers else "L"
        print(f"  {lang.upper()}: [{marker}] {out_name}.tex")

    return pages, containers


def build_include_file(lang, pages, containers):
    titles = SECTION_TITLES_VI if lang == "vi" else SECTION_TITLES_EN

    sections = {}

    for rel_dir, out_name, title, meta in pages:
        sec = rel_dir.split(os.sep)[0]
        sections.setdefault(sec, []).append((rel_dir, out_name, title, meta))

    lines = []

    lines.append(r"\providecommand{\tightlist}{%")
    lines.append(r"  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}%")
    lines.append(r"}")
    lines.append("")

    for sec_dir in sorted(sections, key=lambda s: sort_key(s)):
        sec_pages = sections[sec_dir]
        sec_title = titles.get(sec_dir, sec_dir.replace("-", " "))

        lines.append(f"\\section{{{sanitize_latex_text(sec_title)}}}")
        lines.append("")

        for rel_dir, out_name, title, meta in sec_pages:
            depth = rel_dir.count(os.sep) + 1

            if depth == 1:
                lines.append(f"\\input{{generated/{lang}/{out_name}}}")
                lines.append("")
                continue

            if depth > 1:
                worklog_match = re.match(
                    r"^1-Worklog[\\/](\d+)\.(\d+)-Week(\d+)$",
                    rel_dir,
                )
                blog_match = re.match(
                    r"^3-BlogsPosted[\\/]\d+\.(\d+)-Blog(\d+)$",
                    rel_dir,
                )

                if worklog_match:
                    week = worklog_match.group(3)
                    title = f"Week {week}" if lang == "en" else f"Tuần {week}"
                elif blog_match:
                    blog = blog_match.group(2)
                    title = f"Blog {blog}" if lang == "en" else f"Bài viết {blog}"

                label = (
                    sanitize_latex_text(title)
                    if title
                    else sanitize_latex_text(rel_dir.split(os.sep)[-1].replace("-", " "))
                )

                heading_command = "subsection" if depth == 2 else "subsubsection"
                lines.append(f"\\{heading_command}{{{label}}}")
                lines.append(f"\\input{{generated/{lang}/{out_name}}}")
                lines.append("")

        lines.append(r"\newpage")
        lines.append("")

    out_path = os.path.join(OUTPUT_DIR, f"content_body_{lang}.tex")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  -> {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        check_dependencies()

        print("=== Converting Hugo content to LaTeX ===\n")

        for lang in ("en", "vi"):
            print(f"-- {lang.upper()} --")
            pages, containers = process_language(lang)
            build_include_file(lang, pages, containers)
            print()

        print("Done.")

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)
