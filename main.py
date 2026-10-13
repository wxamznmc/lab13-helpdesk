from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from supabase import Client, create_client


# =========================================================
# Lab 12 Grading — 20 points
# =========================================================
# TODO 1–14: 1 point each
# TODO 15: 2 points (Student-proposed preprocessing)
# TODO 16: 1 point
# Questions 1–3: 1 point each, submitted in <student-id>.pdf
# =========================================================

st.set_page_config(
    page_title="Helpdesk Database Explorer",
    page_icon="🗄️",
    layout="wide",
)

TABLE_NAME = "helpdesk_tickets"

CATEGORIES = [
    "All",
    "Account & Access",
    "Network",
    "Software",
    "Hardware & Peripherals",
]


# =========================================================
# Section 0: Connect Streamlit to Supabase
# =========================================================

# TODO 1:
# Write the complete cache decorator.
# Requirements:
# - use the appropriate Streamlit cache
# - show spinner: "Connecting to Supabase..."
# - show execution time

@st.cache_resource(
    show_spinner="Connecting to Supabase...",
    show_time=True,
)
def init_connection() -> Client:
    url: str = st.secrets["supabase_url"]
    key: str = st.secrets["supabase_key"]

    # TODO 1B:
    # Create and return the Supabase client.
    return create_client(url, key)

supabase = init_connection()


st.title("Helpdesk Database Explorer")
st.caption(
    "Query historical helpdesk tickets directly from Supabase "
    f"• Script reran at {datetime.now().strftime('%H:%M:%S')}"
)


# =========================================================
# Section 1: Practice Supabase queries
# =========================================================
#
# During Query 1–5, test each query before continuing.
# After all five work, move the completed blocks into
# show_query_practice() and remove the original top-level copies.
# =========================================================


# ---------------------------------------------------------
# Run Query practice only when requested
# ---------------------------------------------------------

def show_query_practice():
    # After Query 1–5 work:
    # 1. Move the completed Query 1–5 blocks into this function.
    # 2. Keep each result displayed for checking/grading.
    # 3. Remove the original top-level Query 1–5 blocks above.

    # ---------------------------------------------------------
    # Query 1 — Preview 10 tickets
    # This first query is provided as an example.
    # ---------------------------------------------------------
    preview_response = (
        supabase
        .table(TABLE_NAME)
        .select("*")
        .limit(10)
        .execute()
    )

    preview_df = pd.json_normalize(
        preview_response.data
    )

    st.subheader("Query 1: Ticket preview")
    st.dataframe(
        preview_df,
        hide_index=True,
        width="stretch",
    )

    # ---------------------------------------------------------
    # Query 2 — Select only required columns
    # ---------------------------------------------------------
    recent_response = (
        supabase
        .table(TABLE_NAME)

        # TODO 2A:
        # Select only ticket_id, created_at, category.
        .select("ticket_id, created_at, category")

        # TODO 2B:
        # Order newest first.
        .order("created_at", desc=True)

        # TODO 2C:
        # Return only 10 rows.
        .limit(10)

        # Add your query operations above .execute().
        .execute()
    )

    recent_df = pd.json_normalize(
        getattr(recent_response, "data", [])
    )

    st.subheader("Query 2: Recent ticket metadata")
    st.dataframe(
        recent_df,
        hide_index=True,
        width="stretch",
    )

    # ---------------------------------------------------------
    # Query 3 — Filter by Date range
    # ---------------------------------------------------------
    january_response = (
        supabase
        .table(TABLE_NAME)
        .select("*")

        # TODO 3A:
        # Filter created_at >= 2026-01-01.
        .gte("created_at", "2026-01-01")

        # TODO 3B:
        # Filter created_at < 2026-02-01.
        .lt("created_at", "2026-02-01")

        # Add your query operations above .execute().
        .execute()
    )

    january_df = pd.json_normalize(
        getattr(january_response, "data", [])
    )

    st.subheader("Query 3: January 2026 tickets")
    st.dataframe(
        january_df,
        hide_index=True,
        width="stretch",
    )

    # ---------------------------------------------------------
    # Query 4 — Filter by Category
    # ---------------------------------------------------------
    network_response = (
        supabase
        .table(TABLE_NAME)

        # TODO 4:
        # Complete this query.
        # Requirements are given in the Lab instruction.
        .select("*")
        .eq("category", "Network")
        .order("created_at", desc=True)
        .limit(20)

        # Add your query operations above .execute().
        .execute()
    )

    network_df = pd.json_normalize(
        getattr(network_response, "data", [])
    )

    st.subheader("Query 4: Network tickets")
    st.dataframe(
        network_df,
        hide_index=True,
        width="stretch",
    )

    # ---------------------------------------------------------
    # Query 5 — Combine multiple conditions
    # ---------------------------------------------------------
    combined_response = (
        supabase
        .table(TABLE_NAME)

        # TODO 5A:
        # Select all columns.
        .select("*")

        # TODO 5B:
        # Add the Start date filter.
        .gte("created_at", "2026-01-01")

        # TODO 5C:
        # Add the End date filter.
        .lt("created_at", "2026-02-01")

        # TODO 5D:
        # Add the Category filter.
        .eq("category", "Network")

        # TODO 5E:
        # Order newest first.
        .order("created_at", desc=True)

        # Add your query operations above .execute().
        .execute()
    )

    combined_df = pd.json_normalize(
        getattr(combined_response, "data", [])
    )

    st.subheader("Query 5: January Network tickets")
    st.dataframe(
        combined_df,
        hide_index=True,
        width="stretch",
    )


with st.expander(
    "Database query practice",
    expanded=False,
):
    if st.button(
        "Run practice queries",
        key="run_query_practice",
    ):
        show_query_practice()


# =========================================================
# Section 2: Build a reusable cached query function
# =========================================================

# TODO 6A:
# Write the complete cache decorator.
# Requirements are given in Section 2.1.

@st.cache_data(
    ttl=600,
    show_spinner="Querying helpdesk tickets...",
    show_time=True,
)
def run_query(start_date, end_date, category):
    end_exclusive = end_date + timedelta(days=1)

    query = (
        supabase
        .table(TABLE_NAME)
        .select("*", count="exact")
        .gte(
            "created_at",
            start_date.isoformat(),
        )
        .lt(
            "created_at",
            end_exclusive.isoformat(),
        )
    )

    if category != "All":
        query = query.eq(
            "category",
            category,
        )

    response = query.execute()

    return response.data, response.count


# =========================================================
# Section 3: Connect Streamlit UI to the Database query
# =========================================================

# ---------------------------------------------------------
# 3.1 Load database Date boundaries
# ---------------------------------------------------------

# TODO 7A:
# Write the complete cache decorator.

@st.cache_data(
    ttl=600,
    show_spinner="Loading database date range...",
    show_time=True,
)
def load_date_bounds():
    first_response = (
        supabase
        .table(TABLE_NAME)
        .select("created_at")
        .order("created_at")
        .limit(1)
        .execute()
    )

    last_response = (
        supabase
        .table(TABLE_NAME)
        .select("created_at")
        .order(
            "created_at",
            desc=True,
        )
        .limit(1)
        .execute()
    )

    min_date = pd.to_datetime(
        first_response.data[0]["created_at"]
    ).date()

    max_date = pd.to_datetime(
        last_response.data[0]["created_at"]
    ).date()

    return min_date, max_date


DATA_MIN_DATE, DATA_MAX_DATE = load_date_bounds()


# ---------------------------------------------------------
# 3.2 Create Date and Category controls
# ---------------------------------------------------------

# TODO 8A:
# Set the default end date to a 28-calendar-day range
# starting from DATA_MIN_DATE.
# The value must not be later than DATA_MAX_DATE.
default_end_date = min(
    DATA_MIN_DATE + timedelta(days=27),
    DATA_MAX_DATE,
)


with st.expander(
    "Query filters",
    expanded=True,
):
    start_col, end_col, category_col = st.columns(3)

    with start_col:
        # TODO 8B:
        # Create a date input for the Start date.
        # Requirements:
        # - Default value = DATA_MIN_DATE
        # - Minimum selectable date = DATA_MIN_DATE
        # - Maximum selectable date = DATA_MAX_DATE
        start_date = st.date_input(
            "Start date",
            value=DATA_MIN_DATE,
            min_value=DATA_MIN_DATE,
            max_value=DATA_MAX_DATE,
        )

    with end_col:
        # TODO 8C:
        # Create a date input for the End date.
        # Requirements:
        # - Default value = default_end_date
        # - Minimum selectable date = DATA_MIN_DATE
        # - Maximum selectable date = DATA_MAX_DATE
        end_date = st.date_input(
            "End date",
            value=default_end_date,
            min_value=DATA_MIN_DATE,
            max_value=DATA_MAX_DATE,
        )

    with category_col:
        # TODO 8D:
        # Create a selectbox for Category.
        # Use CATEGORIES as the available options.
        category = st.selectbox(
            "Category",
            CATEGORIES,
        )


# ---------------------------------------------------------
# 3.3 Validate the Date range
# ---------------------------------------------------------

if start_date > end_date:
    # TODO 9:
    # 1. Show an error message explaining that
    #    Start date cannot be later than End date.
    # 2. Stop the current Streamlit run so that
    #    no database query is executed.
    st.error(
        "Start date cannot be later than End date."
    )
    st.stop()


# ---------------------------------------------------------
# 3.4 Connect UI values to run_query()
# ---------------------------------------------------------

records, matching_count = run_query(
    start_date,
    end_date,
    category,
)

df = pd.json_normalize(records)

if "created_at" in df.columns:
    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )


# ---------------------------------------------------------
# 3.5 Manual refresh
# ---------------------------------------------------------

if st.button("Refresh database data"):
    load_date_bounds.clear()
    run_query.clear()
    st.rerun()


# ---------------------------------------------------------
# 3.6 Display the Query result
# ---------------------------------------------------------

matching_count = (
    matching_count
    if matching_count is not None
    else len(df)
)

ticket_col, loaded_col, category_metric_col = (
    st.columns(3)
)

# TODO 10A:
# Show the total number of matching tickets.
ticket_col.metric(
    "Matching Tickets",
    matching_count,
)

# TODO 10B:
# Show the number of rows returned in df.
loaded_col.metric(
    "Rows returned",
    len(df),
)

# TODO 10C:
# Show the category currently selected by the user.
category_metric_col.metric(
    "Selected Category",
    category,
)


if len(df) < matching_count:
    st.warning(
        "More tickets matched the query than were returned. "
        "Use a narrower filter or pagination when the complete "
        "result set is required."
    )

st.subheader("Selected helpdesk tickets")

if df.empty:
    st.info(
        "No tickets matched the selected filters."
    )
else:
    st.dataframe(
        df,
        hide_index=True,
        width="stretch",
    )


# =========================================================
# Section 4: Database Query Challenge
# =========================================================

st.divider()
st.header("5 most recent matching tickets")

# TODO 11:
# Build the Database Query Challenge WITHOUT a template.
#
# Requirements:
# - query helpdesk_tickets
# - use current start_date, end_date, category
# - include all times on end_date
# - if category == "All", do not add a Category filter
# - otherwise filter by the selected Category
# - order newest first
# - return only 5 rows
# - select only ticket_id, created_at, category, text
# - convert the response to a DataFrame and display it
#
# IMPORTANT:
# Filter, sort, and limit at the Database.
# Do not download the whole table and select 5 rows with Pandas.
recent_end_exclusive = end_date + timedelta(days=1)

recent_query = (
    supabase
    .table(TABLE_NAME)
    .select("ticket_id, created_at, category, text")
    .gte("created_at", start_date.isoformat())
    .lt(
        "created_at",
        recent_end_exclusive.isoformat(),
    )
)

if category != "All":
    recent_query = recent_query.eq(
        "category",
        category,
    )

recent_response = (
    recent_query
    .order("created_at", desc=True)
    .limit(5)
    .execute()
)

recent_matching_df = pd.json_normalize(
    recent_response.data
)

st.dataframe(
    recent_matching_df,
    hide_index=True,
    width="stretch",
)


# =========================================================
# Part 2: Preprocess and Persist Training Data
# =========================================================

st.divider()
st.header(
    "Part 2: Preprocess and Persist Training Data"
)


# =========================================================
# Section 5: Load the Complete Training Data
# =========================================================

# TODO 12A:
# Write the complete cache decorator.
# Requirements:
# - cache data
# - ttl = 600 seconds
# - spinner = "Loading complete training data..."
# - show execution time

@st.cache_data(
    ttl=600,
    show_spinner="Loading complete training data...",
    show_time=True,
)
def load_all_training_tickets():
    page_size = 1000
    start = 0
    records = []

    while True:
        # TODO 12B:
        # Query one page of training records.
        # Requirements:
        # - use TABLE_NAME
        # - select ticket_id, created_at, text, category
        # - order by ticket_id
        # - retrieve rows from start to
        #   start + page_size - 1
        response = (
            supabase
            .table(TABLE_NAME)
            .select(
                "ticket_id, created_at, text, category"
            )
            .order("ticket_id")
            .range(
                start,
                start + page_size - 1,
            )
            .execute()
        )

        batch = response.data
        records.extend(batch)

        if len(batch) < page_size:
            break

        start += page_size

    return pd.json_normalize(records)


raw_df = load_all_training_tickets()

st.metric(
    "Raw training tickets",
    len(raw_df),
)


# =========================================================
# Section 6: Remove Boilerplate Phrases
# =========================================================

def preprocess_tickets(df):
    result = df.copy()
    text = result["text"].fillna("").astype(str)

    # TODO 13A:
    # Remove common greeting / opening boilerplate
    # from result["text"].
    text = text.str.replace(
        r"^\s*(?:"
        r"dear customer support(?: team)?|"
        r"hello customer support|"
        r"dear support team|"
        r"to whom it may concern|"
        r")\s*[:,]?\s*",
        "",
        case=False,
        regex=True,
    )

    # TODO 13B:
    # Remove common closing / signature boilerplate.
    text = text.str.replace(
        r"\s*best regards\s*[:,]?\s*(?:name)?\s*$",
        "",
        case=False,
        regex=True,
    )
    text = text.str.replace(
        r"\s*thank you(?: for your [^.?!]*)?[.!]?"
        r"\s*(?:name)?\s*$",
        "",
        case=False,
        regex=True,
    )

    # TODO 14:
    # Normalize whitespace after removing the phrases.
    result["text"] = (
        text
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return result


processed_df = preprocess_tickets(raw_df)


# =========================================================
# Section 7: Inspect the Effect of Boilerplate Removal
# =========================================================
#
# This section is provided.
# It checks whether known boilerplate remains and shows
# a few examples that changed.
# =========================================================

OPENING_BOILERPLATE_PATTERN = (
    r"^\s*(?:"
    r"dear customer support(?: team)?|"
    r"hello customer support|"
    r"dear support team|"
    r"to whom it may concern"
    r")\s*[:,]?\s*"
)

CLOSING_BEST_REGARDS_PATTERN = (
    r"\s*best regards\s*[:,]?\s*(?:name)?\s*$"
)

CLOSING_THANK_YOU_PATTERN = (
    r"\s*thank you(?: for your [^.?!]*)?[.!]?"
    r"\s*(?:name)?\s*$"
)


def summarize_training_data(df):
    text = (
        df["text"]
        .fillna("")
        .astype(str)
    )

    contains_known_boilerplate = (
        text.str.contains(
            OPENING_BOILERPLATE_PATTERN,
            case=False,
            regex=True,
        )
        | text.str.contains(
            CLOSING_BEST_REGARDS_PATTERN,
            case=False,
            regex=True,
        )
        | text.str.contains(
            CLOSING_THANK_YOU_PATTERN,
            case=False,
            regex=True,
        )
    )

    return {
        "Rows": len(df),
        "Known boilerplate remaining": int(
            contains_known_boilerplate.sum()
        ),
        "Average text length": round(
            text.str.len().mean(),
            1,
        ),
    }


summary_df = pd.DataFrame(
    {
        "Raw": summarize_training_data(raw_df),
        "Processed": summarize_training_data(
            processed_df
        ),
    }
)

st.subheader(
    "Boilerplate removal: Before vs After"
)

st.dataframe(
    summary_df,
    width="stretch",
)


changed_mask = (
    raw_df["text"].astype(str)
    != processed_df["text"].astype(str)
)

changed_examples = pd.DataFrame(
    {
        "Raw text": raw_df.loc[
            changed_mask,
            "text",
        ].head(5).values,
        "Processed text": processed_df.loc[
            changed_mask,
            "text",
        ].head(5).values,
    }
)

st.subheader(
    "Examples changed by preprocessing"
)

st.dataframe(
    changed_examples,
    hide_index=True,
    width="stretch",
)


# =========================================================
# Section 8: Student-proposed Preprocessing
# =========================================================

# STEP 1 — Describe your observation
# TODO 15A:
# Describe the preprocessing method and why you selected it.
STUDENT_METHOD = (
    "Normalize HTML line-break markup and anonymized "
    "placeholder variants."
)
STUDENT_REASON = (
    "The training CSV contains <br> markup, "
    "angle-bracket placeholders, and plain "
    "placeholders such as tel_num, acc_num, company_name, "
    "or order_num. Normalizing these template "
    "artifacts may help TF-IDF focus on the technical issue "
    "instead of differences in message formatting."
)


def apply_student_preprocessing(df):
    result = df.copy()

    # STEP 2 — Implement your preprocessing method
    # TODO 15B:
    # Implement one additional preprocessing method.
    text = result["text"].fillna("").astype(str)

    text = text.str.replace(
        r"<br\s*/?>",
        " ",
        case=False,
        regex=True,
    )

    placeholder_tokens = {
        "tel_num": "CONTACT_TOKEN",
        "acc_num": "ACCOUNT_TOKEN",
        "company_name": "COMPANY_TOKEN",
        "order_num": "ORDER_TOKEN",
    }

    for placeholder, token in placeholder_tokens.items():
        text = text.str.replace(
            rf"<?{placeholder}>?",
            token,
            case=False,
            regex=True,
        )

    result["text"] = (
        text
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return result


processed_df = preprocess_tickets(raw_df)
processed_df = apply_student_preprocessing(
    processed_df
)


# STEP 3 — Show your preprocessing decision
st.write(
    "**Student preprocessing:**",
    STUDENT_METHOD,
)
st.write(
    "**Reason:**",
    STUDENT_REASON,
)


# =========================================================
# Section 9: Compare Before and After
# =========================================================

final_summary_df = pd.DataFrame(
    {
        "Raw": summarize_training_data(raw_df),
        "Processed": summarize_training_data(
            processed_df
        ),
    }
)

st.subheader(
    "Final Raw vs Processed data"
)

st.dataframe(
    final_summary_df,
    width="stretch",
)


# =========================================================
# Section 10: Save Processed Data Back to Supabase
# =========================================================
#
# Before using this section:
# Create helpdesk_tickets_processed using the SQL in the
# Lab instruction.
# =========================================================

PROCESSED_TABLE_NAME = (
    "helpdesk_tickets_processed"
)


def save_processed_tickets(
    df,
    batch_size=500,
):
    save_df = df[
        [
            "ticket_id",
            "created_at",
            "text",
            "category",
        ]
    ].copy()

    save_df["created_at"] = pd.to_datetime(
        save_df["created_at"]
    ).dt.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )

    save_df = save_df.where(
        pd.notna(save_df),
        None,
    )

    records = save_df.to_dict(
        orient="records",
    )

    for start in range(
        0,
        len(records),
        batch_size,
    ):
        batch = records[
            start:start + batch_size
        ]

        (
            supabase
            .table(PROCESSED_TABLE_NAME)
            .upsert(
                batch,
                on_conflict="ticket_id",
            )
            .execute()
        )

    return len(records)


if st.button(
    "Save processed training data",
    key="save_processed_training_data",
):
    saved_count = save_processed_tickets(
        processed_df
    )

    st.success(
        f"Saved {saved_count} processed training records."
    )


# =========================================================
# Section 11: Verify the Processed Table
# =========================================================

# This verification block is provided.
processed_response = (
    supabase
    .table(PROCESSED_TABLE_NAME)
    .select(
        "ticket_id, created_at, category, text",
        count="exact",
    )
    .order("ticket_id")
    .limit(10)
    .execute()
)

processed_preview_df = pd.json_normalize(
    processed_response.data
)

processed_table_count = (
    processed_response.count
    if processed_response.count is not None
    else len(processed_preview_df)
)

st.metric(
    "Processed table records",
    processed_table_count,
)

if processed_preview_df.empty:
    st.info(
        "The processed table is empty. "
        "Save the processed training data first."
    )
else:
    st.dataframe(
        processed_preview_df,
        hide_index=True,
        width="stretch",
    )


# =========================================================
# Part 3: Does Preprocessing Improve the Model?
# =========================================================

st.divider()
st.header(
    "Part 3: Raw vs Processed Model Comparison"
)


# =========================================================
# Section 12: Load Experiment Data from Supabase
# =========================================================

# TODO 16A:
# Write the complete cache decorator.
# Requirements:
# - cache data
# - ttl = 600 seconds
# - spinner = "Loading experiment training data..."
# - show execution time

@st.cache_data(
    ttl=600,
    show_spinner="Loading experiment training data...",
    show_time=True,
)
def load_training_table(table_name):
    page_size = 1000
    start = 0
    records = []

    while True:
        # TODO 16B:
        # Query one page from table_name.
        # Requirements:
        # - select ticket_id, text, category
        # - order by ticket_id
        # - retrieve rows from start to
        #   start + page_size - 1
        response = (
            supabase
            .table(table_name)
            .select("ticket_id, text, category")
            .order("ticket_id")
            .range(
                start,
                start + page_size - 1,
            )
            .execute()
        )

        batch = response.data
        records.extend(batch)

        if len(batch) < page_size:
            break

        start += page_size

    return pd.json_normalize(records)


# TODO 16C:
# Write the complete cache decorator.
# Requirements:
# - cache data
# - ttl = 600 seconds
# - spinner = "Loading validation data..."

@st.cache_data(
    ttl=600,
    show_spinner="Loading validation data...",
)
def load_validation_data():
    # TODO 16D:
    # Query helpdesk_validation.
    # Select only query and expected_category.
    response = (
        supabase
        .table("helpdesk_validation")
        .select("query, expected_category")
        .execute()
    )

    return pd.json_normalize(
        response.data
    )


raw_training_df = load_training_table(
    TABLE_NAME
)

processed_training_df = load_training_table(
    PROCESSED_TABLE_NAME
)

validation_df = load_validation_data()


raw_col, processed_col, validation_col = (
    st.columns(3)
)

raw_col.metric(
    "Raw training records",
    len(raw_training_df),
)

processed_col.metric(
    "Processed training records",
    len(processed_training_df),
)

validation_col.metric(
    "Validation queries",
    len(validation_df),
)


# =========================================================
# Section 13: Run a Controlled Model Comparison
# =========================================================
#
# This section is provided.
# Both models use the same settings and validation data.
# Only the training data changes.
# =========================================================

from training import train_model, evaluate_model


NGRAM_RANGE = (1, 2)
REGULARIZATION_C = 1.0


raw_model = train_model(
    tuple(raw_training_df["text"]),
    tuple(raw_training_df["category"]),
    NGRAM_RANGE,
    REGULARIZATION_C,
)

processed_model = train_model(
    tuple(processed_training_df["text"]),
    tuple(processed_training_df["category"]),
    NGRAM_RANGE,
    REGULARIZATION_C,
)


raw_scores, raw_results = evaluate_model(
    raw_model,
    validation_df,
    raw_training_df["category"],
)

processed_scores, processed_results = (
    evaluate_model(
        processed_model,
        validation_df,
        processed_training_df["category"],
    )
)


# =========================================================
# Section 14: Compare the Results
# =========================================================

# ---------------------------------------------------------
# 14.1 Overall Metrics
# ---------------------------------------------------------

comparison_df = pd.DataFrame(
    {
        "Metric": [
            "Accuracy",
            "Macro Precision",
            "Macro Recall",
            "Macro F1",
        ],
        "Raw": [
            raw_scores[
                "validation_accuracy"
            ],
            raw_scores[
                "validation_precision_macro"
            ],
            raw_scores[
                "validation_recall_macro"
            ],
            raw_scores[
                "validation_f1_macro"
            ],
        ],
        "Processed": [
            processed_scores[
                "validation_accuracy"
            ],
            processed_scores[
                "validation_precision_macro"
            ],
            processed_scores[
                "validation_recall_macro"
            ],
            processed_scores[
                "validation_f1_macro"
            ],
        ],
    }
)

comparison_df["Difference"] = (
    comparison_df["Processed"]
    - comparison_df["Raw"]
)

st.subheader(
    "Raw vs Processed: Overall metrics"
)

st.dataframe(
    comparison_df.style.format(
        {
            "Raw": "{:.1%}",
            "Processed": "{:.1%}",
            "Difference": "{:+.1%}",
        }
    ),
    hide_index=True,
    width="stretch",
)


# ---------------------------------------------------------
# 14.2 Scores by Category
# ---------------------------------------------------------

raw_category_df = (
    raw_results["per_category"]
    .rename(
        columns={
            "Precision": "Raw Precision",
            "Recall": "Raw Recall",
            "F1": "Raw F1",
            "Support": "Raw Support",
        }
    )
)

processed_category_df = (
    processed_results["per_category"]
    .rename(
        columns={
            "Precision": "Processed Precision",
            "Recall": "Processed Recall",
            "F1": "Processed F1",
            "Support": "Processed Support",
        }
    )
)

category_comparison_df = (
    raw_category_df.merge(
        processed_category_df,
        on="Category",
    )
)

category_comparison_df[
    "F1 Difference"
] = (
    category_comparison_df[
        "Processed F1"
    ]
    - category_comparison_df[
        "Raw F1"
    ]
)

st.subheader(
    "Raw vs Processed: Scores by Category"
)

st.dataframe(
    category_comparison_df.style.format(
        {
            "Raw Precision": "{:.1%}",
            "Raw Recall": "{:.1%}",
            "Raw F1": "{:.1%}",
            "Processed Precision": "{:.1%}",
            "Processed Recall": "{:.1%}",
            "Processed F1": "{:.1%}",
            "F1 Difference": "{:+.1%}",
        }
    ),
    hide_index=True,
    width="stretch",
)


# ---------------------------------------------------------
# 14.3 Inspect Predictions that Changed
# ---------------------------------------------------------

prediction_comparison_df = validation_df[
    [
        "query",
        "expected_category",
    ]
].copy()

prediction_comparison_df[
    "Raw prediction"
] = (
    raw_results["predictions"][
        "predicted_category"
    ].to_numpy()
)

prediction_comparison_df[
    "Processed prediction"
] = (
    processed_results["predictions"][
        "predicted_category"
    ].to_numpy()
)

prediction_comparison_df[
    "Raw correct"
] = (
    raw_results["predictions"][
        "correct"
    ].to_numpy()
)

prediction_comparison_df[
    "Processed correct"
] = (
    processed_results["predictions"][
        "correct"
    ].to_numpy()
)

changed_predictions_df = (
    prediction_comparison_df.loc[
        prediction_comparison_df[
            "Raw prediction"
        ]
        != prediction_comparison_df[
            "Processed prediction"
        ]
    ].copy()
)

st.metric(
    "Validation predictions changed",
    len(changed_predictions_df),
)

with st.expander(
    "Inspect changed predictions"
):
    st.dataframe(
        changed_predictions_df,
        hide_index=True,
        width="stretch",
    )


# =========================================================
# Final Activity
# =========================================================
#
# The written analysis is submitted separately as:
#
#     <student-id>.pdf
#
# Do NOT write the answers in main.py.
# Follow Section 15 and the Submission checklist in the
# Lab instruction notebook.
# =========================================================
