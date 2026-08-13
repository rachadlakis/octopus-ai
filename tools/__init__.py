# Common tools
from .common_tools import (
    get_current_time,
    get_date,
    web_search,
    fetch_url,
    read_file,
    write_file,
    calculate,
    word_count,
    extract_urls,
    extract_emails,
    json_parse,
    json_format,
    text_replace,
    slugify,
    summarize_stats,
    scrape_webpage,
    extract_html_tables,
)

# Developer tools
from .developer_tools import (
    execute_python,
    execute_shell,
    analyze_code,
    format_code,
    search_documentation,
    generate_gitignore,
    create_dockerfile,
    generate_readme,
    git_status,
    git_log,
    git_diff,
    git_commit,
    git_branch,
    git_checkout,
    git_pull,
    git_push,
    git_stash,
)

# Marketing tools
from .marketing_tools import (
    analyze_readability,
    generate_hashtags,
    create_social_post,
    analyze_headline,
    create_content_calendar,
    generate_cta,
    seo_keyword_analysis,
)

# HR tools
from .hr_tools import (
    generate_job_description,
    parse_resume,
    generate_interview_questions,
    create_onboarding_checklist,
    calculate_salary_range,
    generate_policy_template,
)

# Testing tools
from .testing_tools import (
    run_pytest,
    run_unittest,
    run_jest,
    check_test_coverage,
    generate_test_template,
    analyze_test_quality,
    create_mock_template,
    lint_code,
    generate_test_report,
)

__all__ = [
    # Common
    "get_current_time",
    "get_date",
    "web_search",
    "fetch_url",
    "read_file",
    "write_file",
    "calculate",
    "word_count",
    "extract_urls",
    "extract_emails",
    "json_parse",
    "json_format",
    "text_replace",
    "slugify",
    "summarize_stats",
    "scrape_webpage",
    "extract_html_tables",
    # Developer
    "execute_python",
    "execute_shell",
    "analyze_code",
    "format_code",
    "search_documentation",
    "generate_gitignore",
    "create_dockerfile",
    "generate_readme",
    "git_status",
    "git_log",
    "git_diff",
    "git_commit",
    "git_branch",
    "git_checkout",
    "git_pull",
    "git_push",
    "git_stash",
    # Marketing
    "analyze_readability",
    "generate_hashtags",
    "create_social_post",
    "analyze_headline",
    "create_content_calendar",
    "generate_cta",
    "seo_keyword_analysis",
    # HR
    "generate_job_description",
    "parse_resume",
    "generate_interview_questions",
    "create_onboarding_checklist",
    "calculate_salary_range",
    "generate_policy_template",
    # Testing
    "run_pytest",
    "run_unittest",
    "run_jest",
    "check_test_coverage",
    "generate_test_template",
    "analyze_test_quality",
    "create_mock_template",
    "lint_code",
    "generate_test_report",
]
