# ruff: noqa: E501
import os
from datetime import date, timedelta
from decimal import Decimal
from html import escape

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
st.set_page_config(page_title="WarrantyVault", page_icon="🛡️", layout="wide")
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600&display=swap');
:root{--ink:#33415c;--paper:#fff9f2;--coral:#f26752;--muted:#70758a}
.stApp{background:radial-gradient(circle at 92% 3%,#efeaff 0,transparent 24%),var(--paper)}
.block-container{padding:4rem 2.4rem 3rem;max-width:1160px}.stApp,p,button,input{font-family:'DM Sans',sans-serif}
[data-testid="stSidebar"]{background:#71809b;border-right:0;min-width:235px!important;max-width:235px!important}[data-testid="stSidebar"] *{color:#fffdfa}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:.55rem .7rem;border-radius:10px;margin:.18rem 0}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#8290a8}
.title{font:600 2.8rem/1.05 'Fraunces',serif;color:var(--ink);letter-spacing:-.04em}
.subtitle{color:var(--muted);margin:.55rem 0 2rem}.card{background:rgba(255,255,255,.88);border:1px solid #ebe3da;border-radius:20px;padding:21px 22px;box-shadow:0 10px 30px rgba(36,42,67,.055)}
.label{color:#85899a;font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em}
.value{font:600 1.85rem 'Fraunces',serif;color:var(--ink);margin-top:8px}.hero{position:relative;overflow:hidden;background:#71809b;color:white;border-radius:22px;padding:24px 30px;margin-bottom:16px;min-height:145px}
.hero:after{content:'';position:absolute;width:240px;height:240px;border:52px solid #f26752;opacity:.9;border-radius:50%;right:-65px;top:-86px}
.hero-kicker{color:#ffd0c8;font-size:.7rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase}.hero h2{font:600 2.05rem 'Fraunces',serif;margin:.6rem 0;color:white}.hero p{color:#eef0f5;max-width:590px;margin:0}
.section-label{font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:#8b8895;font-weight:700;margin:2rem 0 .8rem}
.product-card{height:100%;background:white;border:1px solid #ece4db;border-radius:18px;padding:18px;box-shadow:0 8px 24px rgba(32,38,62,.04)}
.product-icon{width:42px;height:42px;display:grid;place-items:center;background:#eee9ff;border-radius:13px;color:#5b4ab0;font-weight:700}.product-card h4{font:600 1.15rem 'Fraunces',serif;color:#33415c;margin:16px 0 4px;overflow-wrap:anywhere}.product-card p{font-size:.78rem;color:#7b7f90;margin:0 0 15px}
.pill{display:inline-block;border-radius:999px;padding:5px 9px;font-size:.68rem;font-weight:700}.active{background:#e6f7ec;color:#26794e}.expiring{background:#fff1d8;color:#9a6511}.expired{background:#feeae7;color:#ad4539}.none{background:#eeeef1;color:#696d79}
.vault-panel{background:#fff;border:1px solid #ebe3da;border-radius:20px;overflow:hidden;box-shadow:0 8px 28px rgba(32,38,62,.045)}
.vault-head{display:flex;justify-content:space-between;align-items:center;padding:16px 20px;background:#f8f4ef;border-bottom:1px solid #ebe3da}.vault-head strong{color:#33415c}.vault-head span{font-size:.74rem;color:#7b7f90}
.vault-list{max-height:295px;overflow-y:auto}.vault-row{display:grid;grid-template-columns:minmax(160px,1.45fr) 1fr .9fr 1.25fr;gap:18px;align-items:center;padding:16px 20px;border-bottom:1px solid #f0e9e2}.vault-row:last-child{border-bottom:0}.vault-product{font-weight:700;color:#33415c;overflow-wrap:anywhere}.vault-meta{font-size:.78rem;color:#7b7f90}.vault-days{font-weight:700;color:#d45b48}.vault-state{justify-self:start;background:#edf6ee;color:#31734d;border-radius:999px;padding:6px 10px;font-size:.68rem;font-weight:700;line-height:1.25;white-space:normal}.vault-state.waiting{background:#f1eff7;color:#716b85}.vault-state.retry{background:#feeae7;color:#ad4539}
.vault-columns{padding:10px 20px;background:#fcfaf7;color:#9294a1;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.attention-row{display:grid;grid-template-columns:1.15fr 1fr 1.25fr;gap:24px;align-items:center;padding:16px 20px;border-bottom:1px solid #f0e9e2}.attention-row:last-child{border-bottom:0}.attention-columns{padding:10px 20px;background:#fcfaf7;color:#9294a1;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em}.attention-main{color:#33415c;font-weight:700}.attention-sub{color:#7b7f90;font-size:.75rem;margin-top:4px}
.detail-card{background:#fff;border:1px solid #ebe3da;border-radius:20px;padding:24px;margin:.8rem 0 0;width:100%;box-sizing:border-box}.detail-status{margin-bottom:22px;padding-bottom:18px;border-bottom:1px solid #f0e9e2}.detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px 48px}.detail-label{font-size:.68rem;text-transform:uppercase;letter-spacing:.09em;color:#9294a1;font-weight:700}.detail-value{margin-top:5px;color:#33415c;font-weight:600;overflow-wrap:anywhere}.product-summary{min-height:205px}.product-summary h3{font:600 1.3rem 'Fraunces',serif;color:#33415c;margin:.8rem 0 .2rem;min-height:32px;overflow-wrap:anywhere}.product-summary .expiry{font-size:.82rem;color:#70758a;min-height:48px;margin:.8rem 0}
.auth-banner{background:#eef1f7;border:1px solid #dce2ef;border-radius:24px;padding:26px 30px;color:#33415c;margin:2rem 0 1.3rem}.auth-banner small{color:#d75a49;text-transform:uppercase;letter-spacing:.12em}.auth-banner h2{font:600 2rem 'Fraunces',serif;margin:.6rem 0}.auth-banner p{color:#68738a;margin:0}
.stButton>button,.stFormSubmitButton>button{border-radius:10px;border:0;background:#f26752;color:white;font-weight:700;min-height:42px;white-space:normal}.stButton>button:hover,.stFormSubmitButton>button:hover{background:#d95341;color:white;border:0}
[data-testid="stBaseButton-tertiary"]{background:transparent!important;color:#526079!important;padding-left:0!important;min-height:auto!important}[data-testid="stBaseButton-tertiary"]:hover{background:transparent!important;color:#f26752!important}
@media(max-width:850px){.block-container{padding:3.5rem 1rem 2rem}.vault-row,.attention-row{grid-template-columns:1fr;gap:10px}.vault-columns,.attention-columns{display:none}.detail-grid{grid-template-columns:1fr}.title{font-size:2.2rem}}
[data-testid="stDataFrame"]{border:1px solid #ebe3da;border-radius:16px;overflow:hidden;background:white}[data-testid="stExpander"]{border:1px solid #ebe3da!important;border-radius:16px!important;background:rgba(255,255,255,.72)}
</style>""",
    unsafe_allow_html=True,
)


def api(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    if st.session_state.get("token"):
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        response = requests.request(method, API_URL + path, headers=headers, timeout=90, **kwargs)
    except requests.ConnectionError:
        st.error("Start the FastAPI backend at http://localhost:8000 first.")
        return None
    if not response.ok:
        try:
            detail = response.json().get("detail", "Request failed")
        except ValueError:
            detail = f"Backend error ({response.status_code}). Check the FastAPI terminal for details."
        if isinstance(detail, list):
            detail = "\n".join(
                f"{' → '.join(str(part) for part in error.get('loc', []) if part != 'body')}: {error.get('msg', 'Invalid value')}"
                for error in detail
            )
        st.error(detail)
        return None
    return None if response.status_code == 204 else response.json()


def set_success(message):
    """Keep confirmation visible after Streamlit reruns the page."""
    st.session_state.success_message = message


def show_success():
    message = st.session_state.pop("success_message", None)
    if message:
        st.toast(message, duration="short")


def login(email, password):
    result = api("POST", "/auth/login", data={"username": email, "password": password})
    if result:
        st.session_state.token = result["access_token"]
        st.rerun()


def auth_page():
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown("<br><div class='title'>WarrantyVault.</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='subtitle'>A personal archive for the things worth protecting.</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='auth-banner'><small>Private by design</small><h2>Keep the proof.<br>Never miss an expiry.</h2><p>Products, claim details and documents—ready when something breaks.</p></div>",
            unsafe_allow_html=True,
        )
        sign_in, sign_up = st.tabs(["Sign in", "Create account"])
        with sign_in:
            with st.form("login"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Sign in", type="primary", use_container_width=True):
                    login(email, password)
        with sign_up:
            with st.form("signup"):
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                if st.form_submit_button("Create account", type="primary", use_container_width=True):
                    if api("POST", "/auth/signup", json={"email": email, "password": password}):
                        login(email, password)


def get_products():
    result = api("GET", "/products?page_size=100")
    return result.get("items", []) if result else []


def warranty_status(product):
    expiry = (
        date.fromisoformat(product["warranty_expiry_date"]) if product.get("warranty_expiry_date") else None
    )
    if not expiry:
        return "No warranty"
    days = (expiry - date.today()).days
    if days < 0:
        return "Expired"
    return "Expiring soon" if days <= 30 else "Active"


def display_date(value):
    return date.fromisoformat(value).strftime("%-d %b %Y") if value else "—"


def display_price(value):
    if value is None:
        return "—"
    digits = str(int(Decimal(value).quantize(Decimal("1"))))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        groups = []
        while head:
            groups.insert(0, head[-2:])
            head = head[:-2]
        digits = f"{','.join(groups)},{tail}"
    return f"₹{digits}"


def expiry_message(product):
    if not product.get("warranty_expiry_date"):
        return "Warranty details incomplete"
    expiry = date.fromisoformat(product["warranty_expiry_date"])
    days = (expiry - date.today()).days
    if days == 1:
        return "Expires tomorrow"
    if days == 0:
        return "Expires today"
    if days > 1:
        return f"Expires in {days} days"
    return f"Expired {abs(days)} days ago"


def show_products(items):
    if not items:
        st.info("No products yet. Add your first product to start tracking its warranty.")
        return
    rows = [
        {
            "Product": item["product_name"],
            "Brand": item.get("brand") or "—",
            "Purchased from": item.get("seller") or "—",
            "Purchased": item.get("purchase_date") or "—",
            "Warranty": warranty_status(item),
            "Expiry": item.get("warranty_expiry_date") or "—",
        }
        for item in items
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)


def show_product_cards(items):
    if not items:
        st.info("No products yet. Add your first product to start tracking its warranty.")
        return
    columns = st.columns(min(3, len(items)))
    for index, item in enumerate(items):
        status = warranty_status(item)
        tone = "expiring" if status == "Expiring soon" else "active" if status == "Active" else "expired" if status == "Expired" else "none"
        with columns[index % len(columns)]:
            name = escape(item["product_name"])
            brand = escape((item.get("brand") or "Unbranded").title())
            st.markdown(
                f"<div class='product-card'><div class='product-icon'>{name[:1].upper()}</div><h4>{name}</h4><p>{brand}</p><span class='pill {tone}'>{status}</span></div>",
                unsafe_allow_html=True,
            )


def dashboard():
    st.markdown("<div class='title'>Your warranties, all in one place.</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Keep purchase proof, claim details, and upcoming expirations organized.</div>",
        unsafe_allow_html=True,
    )
    summary = api("GET", "/analytics/summary?expiring_within_days=30")
    if not summary:
        return
    active, expiring = summary["active_warranties"], summary["expiring_soon"]
    expiring_products = api("GET", "/products/expiring?days=30") or []
    if summary["total_products"] == 0:
        headline, message = "Your vault is ready", "Add your first product to start tracking its warranty."
    elif expiring_products:
        nearest = min(expiring_products, key=lambda item: item["warranty_expiry_date"])
        headline = f"{expiring} {'warranty needs' if expiring == 1 else 'warranties need'} your attention"
        message = f"Your next warranty {expiry_message(nearest).lower()}."
    else:
        headline, message = "Everything is on track", "No warranties expire in the next 30 days."
    st.markdown(
        f"<div class='hero'><div class='hero-kicker'>Warranty overview</div><h2>{headline}</h2><p>{message}</p></div>",
        unsafe_allow_html=True,
    )
    metrics = [
        ("Products", summary["total_products"]),
        ("Active", active),
        ("Expiring soon", expiring),
        ("Expired", summary["expired_warranties"]),
    ]
    for column, (label, value) in zip(st.columns(4), metrics, strict=True):
        column.markdown(
            f"<div class='card'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div class='section-label'>Upcoming expirations</div>", unsafe_allow_html=True)
    notifications = api("GET", "/notifications") or []
    if expiring_products:
        upcoming_rows = []
        for product in sorted(expiring_products, key=lambda item: item["warranty_expiry_date"]):
            expiry = date.fromisoformat(product["warranty_expiry_date"])
            days = (expiry - date.today()).days
            preferences = api("GET", f"/products/{product['id']}/reminders") or {"days_before": []}
            current_history = [
                item for item in notifications
                if item["product_id"] == product["id"]
                and item["warranty_expiry_date"] == product["warranty_expiry_date"]
                and item["days_before"] in preferences["days_before"]
            ]
            sent = next((item for item in current_history if item["status"] == "sent"), None)
            future_dates = sorted(
                (expiry - timedelta(days=day), day)
                for day in preferences["days_before"]
                if expiry - timedelta(days=day) >= date.today()
            )
            if sent or not future_dates:
                continue
            wait = (future_dates[0][0] - date.today()).days
            next_reminder_date = future_dates[0][0]
            reminder_days = future_dates[0][1]
            upcoming_rows.append(
                "<div class='attention-row'>"
                f"<div><div class='vault-product'>{escape(product['product_name'])}</div>"
                f"<div class='vault-meta'>{escape((product.get('brand') or 'Unbranded').title())}</div></div>"
                f"<div><div class='attention-main'>{expiry_message(product)}</div>"
                f"<div class='attention-sub'>{expiry.strftime('%-d %b %Y')}</div></div>"
                f"<div><div class='attention-main'>{'Due today' if wait == 0 else next_reminder_date.strftime('%-d %b %Y')}</div>"
                f"<div class='attention-sub'>Email · {reminder_days} {'day' if reminder_days == 1 else 'days'} before</div></div>"
                "</div>"
            )
        if upcoming_rows:
            st.markdown(
                "<div class='vault-panel'>"
                f"<div class='vault-head'><div><strong>Needs your attention</strong><div class='vault-meta'>Scheduled warranty emails</div></div><span>{len(upcoming_rows)} scheduled</span></div>"
                "<div class='attention-row attention-columns'><div>Product</div><div>Warranty</div><div>Next reminder</div></div>"
                f"<div class='vault-list'>{''.join(upcoming_rows)}</div></div>",
                unsafe_allow_html=True,
            )
        else:
            st.caption("No scheduled reminders for warranties expiring in the next 30 days.")
    else:
        st.caption("No warranties expire in the next 30 days.")
    st.markdown("<div class='section-label'>Recently added</div>", unsafe_allow_html=True)
    show_product_cards(get_products()[:6])


def reminder_choices(prefix):
    columns = st.columns(3)
    return [
        day
        for day, checked in [
            (30, columns[0].checkbox("30 days", True, key=f"{prefix}_30")),
            (7, columns[1].checkbox("7 days", True, key=f"{prefix}_7")),
            (1, columns[2].checkbox("1 day", False, key=f"{prefix}_1")),
        ]
        if checked
    ]


def extraction_review():
    preview = st.session_state.get("extraction_preview")
    if not preview:
        return
    items = preview.get("items", [])
    st.markdown("<div class='section-label'>Review detected items</div>", unsafe_allow_html=True)
    st.info("Choose the real products and correct any details. Delivery fees, discounts, and other lines can be excluded.")
    with st.form("confirm_extraction"):
        left, right = st.columns(2)
        seller = left.text_input("Purchased from", preview.get("seller") or "")
        invoice = right.text_input("Invoice number", preview.get("invoice_number") or "")
        purchased_value = (
            date.fromisoformat(preview["purchase_date"]) if preview.get("purchase_date") else None
        )
        purchased = left.date_input("Purchase date", value=purchased_value)
        reviewed = []
        for index, item in enumerate(items):
            with st.container(border=True):
                include = st.checkbox(
                    f"Include item {index + 1}", True, key=f"extract_include_{index}"
                )
                item_left, item_right = st.columns(2)
                name = item_left.text_input(
                    "Product name *", item.get("product_name") or "", key=f"extract_name_{index}"
                )
                brand = item_right.text_input(
                    "Brand", item.get("brand") or "", key=f"extract_brand_{index}"
                )
                price = item_left.number_input(
                    "Price",
                    min_value=0.0,
                    value=float(item["price"]) if item.get("price") is not None else None,
                    key=f"extract_price_{index}",
                )
                serial = item_right.text_input(
                    "Serial number", item.get("serial_number") or "", key=f"extract_serial_{index}"
                )
                warranty_months = item_left.number_input(
                    "Warranty months",
                    min_value=0,
                    value=item.get("warranty_months"),
                    step=1,
                    key=f"extract_warranty_{index}",
                )
                expiry = item_right.date_input(
                    "Warranty expires", value=None, key=f"extract_expiry_{index}"
                )
                reviewed.append(
                    {
                        "include": include,
                        "product_name": name,
                        "brand": brand or None,
                        "price": price,
                        "serial_number": serial or None,
                        "warranty_months": warranty_months,
                        "warranty_expiry_date": expiry.isoformat() if expiry else None,
                    }
                )
        st.caption("Notify me before expiry")
        days = reminder_choices("extract")
        confirm, discard = st.columns(2)
        if confirm.form_submit_button("Save selected products", type="primary"):
            products = [
                {
                    **{key: value for key, value in item.items() if key != "include"},
                    "seller": seller or None,
                    "purchase_date": purchased.isoformat() if purchased else None,
                    "invoice_number": invoice or None,
                }
                for item in reviewed
                if item["include"] and item["product_name"].strip()
            ]
            if not products:
                st.warning("Select at least one product before saving.")
                st.stop()
            payload = {
                "products": products,
                "reminder_days": days,
            }
            saved = api("POST", f"/documents/{preview['document']['id']}/confirm", json=payload)
            if saved:
                del st.session_state.extraction_preview
                set_success(f"Saved {len(saved)} products and linked this invoice to each one.")
                st.rerun()
        if discard.form_submit_button("Discard"):
            del st.session_state.extraction_preview
            st.rerun()


def add_product_section():
    manual, invoice = st.tabs(["Add manually", "Upload invoice to prefill"])
    with manual:
        with st.form("add_product", clear_on_submit=True):
            left, right = st.columns(2)
            name, brand = left.text_input("Product name *"), right.text_input("Brand")
            category, seller = left.text_input("Category"), right.text_input("Purchased from")
            purchased = left.date_input("Purchase date", value=None)
            price = right.number_input("Price", min_value=0.0, value=None)
            expiry = left.date_input("Warranty expires", value=None)
            serial = right.text_input("Serial number")
            invoice_number = left.text_input("Invoice number")
            provider = right.text_input("Warranty provider")
            support_url = left.text_input("Support URL")
            support_phone = right.text_input("Support phone")
            support_email = left.text_input("Support email")
            notes = st.text_area("Notes")
            st.caption("Notify me before expiry")
            days = reminder_choices("manual")
            if st.form_submit_button("Save product", type="primary"):
                payload = {
                    "product_name": name,
                    "brand": brand or None,
                    "category": category or None,
                    "seller": seller or None,
                    "purchase_date": purchased.isoformat() if purchased else None,
                    "price": price,
                    "warranty_expiry_date": expiry.isoformat() if expiry else None,
                    "serial_number": serial or None,
                    "invoice_number": invoice_number or None,
                    "warranty_provider": provider or None,
                    "support_url": support_url or None,
                    "support_phone": support_phone or None,
                    "support_email": support_email or None,
                    "notes": notes or None,
                }
                product = api("POST", "/products", json=payload)
                if product:
                    api("PUT", f"/products/{product['id']}/reminders", json={"days_before": days})
                    set_success("Product saved successfully.")
                    st.rerun()
    with invoice:
        with st.form("invoice_upload", clear_on_submit=True):
            upload = st.file_uploader("Receipt or invoice PDF", type=["pdf"])
            st.caption("WarrantyVault will read the PDF and prefill any details it can identify.")
            if st.form_submit_button("Extract invoice details", type="primary"):
                if not upload:
                    st.warning("Choose an invoice PDF first.")
                else:
                    with st.spinner("Reading your receipt and fetching product details...", show_time=True):
                        document = api(
                            "POST",
                            "/documents",
                            files={"file": (upload.name, upload.getvalue(), upload.type)},
                        )
                        if document:
                            preview = api("POST", f"/documents/{document['id']}/extract")
                            if preview:
                                st.session_state.extraction_preview = preview
                                st.rerun()
        extraction_review()


def edit_product(product):
    with st.form("edit_product"):
        left, right = st.columns(2)
        name = left.text_input("Product name", product["product_name"])
        brand = right.text_input("Brand", product.get("brand") or "")
        category = left.text_input("Category", product.get("category") or "")
        seller = right.text_input("Purchased from", product.get("seller") or "")
        purchased_value = (
            date.fromisoformat(product["purchase_date"]) if product.get("purchase_date") else None
        )
        purchased = left.date_input("Purchase date", value=purchased_value)
        price = right.number_input(
            "Price",
            min_value=0.0,
            value=float(product["price"]) if product.get("price") is not None else None,
        )
        expiry_value = (
            date.fromisoformat(product["warranty_expiry_date"])
            if product.get("warranty_expiry_date")
            else None
        )
        expiry = left.date_input("Warranty expires", value=expiry_value)
        serial = right.text_input("Serial number", product.get("serial_number") or "")
        invoice_number = left.text_input("Invoice number", product.get("invoice_number") or "")
        provider = right.text_input("Warranty provider", product.get("warranty_provider") or "")
        support_url = left.text_input("Support URL", product.get("support_url") or "")
        support_phone = right.text_input("Support phone", product.get("support_phone") or "")
        support_email = left.text_input("Support email", product.get("support_email") or "")
        notes = st.text_area("Notes", product.get("notes") or "")
        save, remove = st.columns(2)
        if save.form_submit_button("Save changes", type="primary"):
            payload = {
                "product_name": name,
                "brand": brand or None,
                "category": category or None,
                "seller": seller or None,
                "purchase_date": purchased.isoformat() if purchased else None,
                "price": price,
                "warranty_expiry_date": expiry.isoformat() if expiry else None,
                "serial_number": serial or None,
                "invoice_number": invoice_number or None,
                "warranty_provider": provider or None,
                "support_url": support_url or None,
                "support_phone": support_phone or None,
                "support_email": support_email or None,
                "notes": notes or None,
            }
            if api("PATCH", f"/products/{product['id']}", json=payload):
                st.session_state.editing_product = False
                set_success("Your product changes were saved.")
                st.rerun()
        if remove.form_submit_button("Delete product"):
            api("DELETE", f"/products/{product['id']}")
            st.session_state.selected_product_id = None
            st.session_state.editing_product = False
            set_success("Product deleted.")
            st.rerun()


def product_documents(product):
    st.markdown("#### Purchase & warranty documents")
    st.caption(
        "Keep invoices, receipts, warranty cards, and other proof associated with this product."
    )
    with st.expander("＋ Add document"):
        with st.form("attach_document", clear_on_submit=True):
            upload = st.file_uploader("Choose PDF or image", type=["pdf", "jpg", "jpeg", "png"])
            if st.form_submit_button("Save with this product", type="primary"):
                if not upload:
                    st.warning("Choose a file first.")
                elif api(
                    "POST",
                    "/documents",
                    data={"product_id": product["id"]},
                    files={"file": (upload.name, upload.getvalue(), upload.type)},
                ):
                    set_success(f"{upload.name} was saved with {product['product_name']}.")
                    st.rerun()
    documents = api("GET", f"/documents?product_id={product['id']}") or []
    if not documents:
        st.info("No documents yet. Add an invoice, receipt, warranty card, or other proof you may need for a claim.")
    for document in documents:
        response = requests.get(
            API_URL + f"/documents/{document['id']}/download",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=30,
        )
        if response.ok:
            with st.container(border=True):
                name, download, remove = st.columns([5, 2, 1])
                name.markdown(f"**{document['original_filename']}**")
                name.caption(f"Saved {document['created_at'][:10]} · {document['size_bytes'] / 1024:.1f} KB")
                download.download_button(
                    "Download",
                    response.content,
                    file_name=document["original_filename"],
                    mime=document["content_type"],
                    key=f"download_{document['id']}",
                    use_container_width=True,
                )
                if remove.button("Delete", key=f"delete_document_{document['id']}"):
                    api("DELETE", f"/documents/{document['id']}")
                    set_success(f"{document['original_filename']} was deleted.")
                    st.rerun()


def product_detail(product):
    if st.button("← Products", type="tertiary"):
        st.session_state.selected_product_id = None
        st.session_state.editing_product = False
        st.rerun()
    heading, action = st.columns([4, 1.2])
    heading.markdown(f"<div class='title'>{escape(product['product_name'])}</div>", unsafe_allow_html=True)
    heading.markdown(
        f"<div class='subtitle'>{escape(product.get('brand') or 'Unbranded')}</div>",
        unsafe_allow_html=True,
    )
    if action.button("Edit product", use_container_width=True):
        st.session_state.editing_product = not st.session_state.get("editing_product", False)
        st.rerun()
    if st.session_state.get("editing_product"):
        edit_product(product)
        return

    overview, documents = st.tabs(["Overview", "Documents"])
    with overview:
        status = warranty_status(product)
        tone = "expiring" if status == "Expiring soon" else "active" if status == "Active" else "expired" if status == "Expired" else "none"
        status_label = status if status != "No warranty" else "Warranty details incomplete"
        fields = [
            ("Purchased", display_date(product.get("purchase_date"))),
            ("Warranty", display_date(product.get("warranty_expiry_date"))),
            ("Price", display_price(product.get("price"))),
            ("Serial number", product.get("serial_number") or "—"),
            ("Purchased from", product.get("seller") or "—"),
            ("Invoice number", product.get("invoice_number") or "—"),
            ("Warranty provider", product.get("warranty_provider") or "—"),
            ("Support", product.get("support_url") or product.get("support_email") or product.get("support_phone") or "—"),
        ]
        cells = "".join(
            f"<div><div class='detail-label'>{escape(label)}</div><div class='detail-value'>{escape(str(value))}</div></div>"
            for label, value in fields
        )
        st.markdown(
            f"<div class='detail-card'><div class='detail-status'><span class='pill {tone}'>{status_label}</span></div>"
            f"<div class='detail-grid'>{cells}</div></div>",
            unsafe_allow_html=True,
        )
        if product.get("notes"):
            st.markdown(f"<div class='detail-card'><div class='detail-label'>Notes</div><div class='detail-value'>{escape(product['notes'])}</div></div>", unsafe_allow_html=True)
    with documents:
        product_documents(product)


def product_page():
    items = get_products()
    selected_id = st.session_state.get("selected_product_id")
    selected_product = next((item for item in items if item["id"] == selected_id), None)
    if selected_product:
        product_detail(selected_product)
        return
    st.markdown(
        "<div class='title'>Products</div><div class='subtitle'>Everything needed for a warranty claim, together.</div>",
        unsafe_allow_html=True,
    )
    with st.expander("＋ Add product"):
        add_product_section()
    if not items:
        st.info("No products yet. Add your first product to start tracking its warranty.")
        return
    search, filters = st.columns([2, 1.4])
    query = search.text_input("Search your products", placeholder="Search by product or brand...")
    selected_filter = filters.radio(
        "Warranty status", ["All", "Active", "Expired", "Incomplete"], horizontal=True
    )
    filtered = []
    for product in items:
        matches_query = query.lower() in f"{product['product_name']} {product.get('brand') or ''}".lower()
        status = warranty_status(product)
        matches_filter = selected_filter == "All" or (
            selected_filter == "Incomplete" and status == "No warranty"
        ) or status == selected_filter or (selected_filter == "Active" and status == "Expiring soon")
        if matches_query and matches_filter:
            filtered.append(product)
    if not filtered:
        st.info("No products match your search.")
        return
    columns = st.columns(2)
    for index, product in enumerate(filtered):
        with columns[index % 2]:
            with st.container(border=True):
                name = escape(product["product_name"])
                brand = escape((product.get("brand") or "Unbranded").title())
                status = warranty_status(product)
                tone = "expiring" if status == "Expiring soon" else "active" if status == "Active" else "expired" if status == "Expired" else "none"
                st.markdown(
                    f"<div class='product-summary'><div class='product-icon'>{name[:1].upper()}</div>"
                    f"<h3>{name}</h3><div class='vault-meta'>{brand}</div>"
                    f"<div class='expiry'>{escape(expiry_message(product))}<br>{display_date(product.get('warranty_expiry_date'))}</div>"
                    f"<span class='pill {tone}'>{'Details incomplete' if status == 'No warranty' else status}</span></div>",
                    unsafe_allow_html=True,
                )
                if st.button("View details →", key=f"view_product_{product['id']}", use_container_width=True):
                    st.session_state.selected_product_id = product["id"]
                    st.session_state.editing_product = False
                    st.rerun()


def notifications_page():
    st.markdown(
        "<div class='title'>Reminders</div><div class='subtitle'>Warranty deadlines that need your attention.</div>",
        unsafe_allow_html=True,
    )
    products = get_products()
    account_settings = api("GET", "/auth/me/reminders") or {
        "email": "",
        "reminder_email_enabled": True,
    }
    if products:
        with st.expander("Reminder settings"):
            choices = {f"{p['product_name']} — {p.get('brand') or 'Unbranded'}": p["id"] for p in products}
            selected = st.selectbox("Product", list(choices), key="reminder_product")
            current = api("GET", f"/products/{choices[selected]}/reminders") or {"days_before": [30, 7]}
            with st.form("reminder_preferences"):
                st.markdown("**Email me before this warranty expires**")
                columns = st.columns(3)
                day_30 = columns[0].checkbox("30 days before", 30 in current["days_before"])
                day_7 = columns[1].checkbox("7 days before", 7 in current["days_before"])
                day_1 = columns[2].checkbox("1 day before", 1 in current["days_before"])
                email = account_settings["email"]
                if email:
                    name, domain = email.split("@", 1)
                    masked = f"{name[:3]}{'•' * max(3, len(name) - 3)}@{domain}"
                    st.caption(f"Reminders will be sent to {masked}")
                if st.form_submit_button("Save reminder settings"):
                    days = [day for day, enabled in [(30, day_30), (7, day_7), (1, day_1)] if enabled]
                    saved_days = api("PUT", f"/products/{choices[selected]}/reminders", json={"days_before": days})
                    if saved_days:
                        set_success("Reminder preferences saved.")
                        st.rerun()
    notifications = api("GET", "/notifications") or []
    products_with_warranties = [product for product in products if product.get("warranty_expiry_date")]
    if not products_with_warranties:
        st.info("Add a warranty expiry date to schedule reminders.")
        return
    products_by_id = {product["id"]: product for product in products}
    upcoming_rows = []
    for product in products_with_warranties:
        preferences = api("GET", f"/products/{product['id']}/reminders") or {"days_before": []}
        expiry = date.fromisoformat(product["warranty_expiry_date"])
        for days_before in preferences["days_before"]:
            scheduled_for = expiry - timedelta(days=days_before)
            already_sent = any(
                notification["product_id"] == product["id"]
                and notification["warranty_expiry_date"] == product["warranty_expiry_date"]
                and notification["days_before"] == days_before
                and notification["status"] == "sent"
                for notification in notifications
            )
            if scheduled_for >= date.today() and not already_sent:
                upcoming_rows.append((scheduled_for, product, days_before))

    upcoming, sent = st.tabs(["Upcoming", "Recently sent"])
    with upcoming:
        if not upcoming_rows:
            st.info("No email reminders are currently scheduled.")
        else:
            rows = []
            for scheduled_for, product, days_before in sorted(upcoming_rows, key=lambda item: item[0]):
                rows.append(
                    "<div class='vault-row'>"
                    f"<div><div class='vault-product'>{escape(product['product_name'])}</div>"
                    f"<div class='vault-meta'>Warranty expires {display_date(product['warranty_expiry_date'])}</div></div>"
                    f"<div class='vault-meta'>Reminder on<br><b>{scheduled_for.strftime('%-d %b %Y')}</b></div>"
                    f"<div class='vault-meta'>{days_before} {'day' if days_before == 1 else 'days'} before</div>"
                    "<div class='vault-state waiting'>Scheduled</div></div>"
                )
            st.markdown(f"<div class='vault-panel'><div class='vault-list'>{''.join(rows)}</div></div>", unsafe_allow_html=True)
    with sent:
        sent_notifications = [item for item in notifications if item["status"] == "sent"]
        if not sent_notifications:
            st.info("No email reminders have been sent yet.")
        else:
            rows = []
            for notification in sent_notifications[:20]:
                product = products_by_id.get(notification["product_id"])
                if not product:
                    continue
                sent_on = notification["sent_at"][:10] if notification.get("sent_at") else notification["scheduled_for"]
                rows.append(
                    "<div class='vault-row'>"
                    f"<div><div class='vault-product'>{escape(product['product_name'])}</div>"
                    f"<div class='vault-meta'>Warranty expires {display_date(notification['warranty_expiry_date'])}</div></div>"
                    f"<div class='vault-meta'>Sent {display_date(sent_on)}</div>"
                    f"<div class='vault-meta'>{notification['days_before']}-day reminder</div>"
                    "<div class='vault-state'>Email sent</div></div>"
                )
            st.markdown(f"<div class='vault-panel'><div class='vault-list'>{''.join(rows)}</div></div>", unsafe_allow_html=True)


st.session_state.setdefault("token", "")
if not st.session_state.token:
    auth_page()
else:
    with st.sidebar:
        st.markdown("## WARRANTYVAULT")
        st.caption("Your warranties, organized.")
        page = st.radio("Navigation", ["Dashboard", "Products", "Reminders"], label_visibility="collapsed")
        st.divider()
        if st.button("Sign out"):
            st.session_state.token = ""
            st.rerun()
    show_success()
    {"Dashboard": dashboard, "Products": product_page, "Reminders": notifications_page}[page]()
