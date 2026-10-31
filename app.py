import math

import pandas as pd
import streamlit as st
from sectors import SectorsError, get_company_overview

st.set_page_config(page_title="TUMBUH | Investment Goal Calculator")

st.markdown(
	"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

	:root {
		--bg: #100d0e;
		--surface: #1e191a;
		--ink: #f6f1ee;
		--muted: #b4a9a7;
		--pink: #e5337e;
		--gold: #df9439;
		--green: #1fb36a;
		--line: rgba(246, 241, 238, 0.14);
	}
	.stApp {
		background: linear-gradient(135deg, #171116 0%, var(--bg) 48%, #18120e 100%);
		color: var(--ink);
	}
	[data-testid="stSidebar"] {
		background: rgba(16, 13, 14, 0.96);
		border-right: 1px solid var(--line);
	}
	[data-testid="stSidebar"] input[type="radio"] { accent-color: var(--pink); }
	.block-container { max-width: 760px; padding-top: 2.4rem; padding-bottom: 3rem; }
	[data-testid="stHeader"] { background: transparent; }
	h1, h2, h3, p, label { color: var(--ink); }
	h1 { font-family: 'DM Serif Display', Georgia, serif; font-weight: 400; }
	body, [class*="st-"], button, input {
		font-family: 'Plus Jakarta Sans', sans-serif;
	}
	.brandbar { display: flex; align-items: center; gap: 12px; margin-bottom: 1.8rem; }
	.brandmark {
		width: 46px; height: 46px; flex: none; border-radius: 12px;
		background: linear-gradient(135deg, var(--pink), var(--gold));
		box-shadow: 0 8px 26px rgba(229, 51, 126, 0.25);
		display: grid; place-items: center;
	}
	.brandname { color: var(--ink); font-size: 0.95rem; font-weight: 700; }
	.brandtag {
		color: var(--muted); font-size: 0.65rem; font-weight: 600;
		letter-spacing: 0.12em; text-transform: uppercase; margin-top: 2px;
	}
	[data-testid="stTextInput"] input {
		background: var(--surface); color: var(--ink);
		border-color: var(--line); border-radius: 8px;
	}
	.stButton button {
		background: var(--pink); color: white; border: 0; border-radius: 8px;
	}
	.side-brand { color: var(--ink); font-size: 1.15rem; font-weight: 700; }
	.side-brand span { color: var(--pink); }
	.side-section {
		color: var(--muted); font-size: 0.65rem; font-weight: 700;
		letter-spacing: 0.12em; margin: 1.5rem 0 0.5rem;
	}
	[data-testid="stNumberInput"] input {
		background: var(--surface); color: var(--ink);
		border-color: var(--line); border-radius: 8px;
	}
	[data-testid="stNumberInput"] button {
		background: var(--surface); color: var(--gold); border-color: var(--line);
	}
	div[data-testid="stMetric"] {
		background: linear-gradient(115deg, rgba(229, 51, 126, 0.18), rgba(223, 148, 57, 0.12));
		border: 1px solid rgba(229, 51, 126, 0.35); border-radius: 12px;
		padding: 1.1rem 1.25rem;
	}
	[data-testid="stMetricLabel"] { color: var(--muted); }
	[data-testid="stMetricValue"] {
		color: var(--ink); font-family: 'DM Serif Display', Georgia, serif;
		font-size: 2.2rem; overflow-wrap: anywhere;
	}
	.stCaption { color: var(--muted); }
	hr { border-color: var(--line); }
	</style>
	""",
	unsafe_allow_html=True,
)

st.sidebar.markdown(
	'<div class="side-brand">TUMBUH<span>.</span></div>'
	'<div class="side-section">NAVIGASI</div>',
	unsafe_allow_html=True,
)
selected_menu = st.sidebar.radio(
	"Menu",
	["Ringkasan", "Watchlist", "Portofolio", "Pasar", "Kalkulator", "Berita", "Belajar"],
	index=4,
	label_visibility="collapsed",
)

if selected_menu != "Kalkulator":
	st.title(selected_menu)
	st.info(f"Bagian {selected_menu} belum tersedia.")
	st.stop()


def format_rupiah(amount):
	return f"Rp {round(amount):,}".replace(",", ".")


def project_growth(monthly_saving, years, yearly_return):
	monthly_return = (1 + yearly_return / 100) ** (1 / 12) - 1
	balance = 0.0
	yearly_totals = [{"Year": 0, "Total (Rp)": balance}]

	for month in range(1, years * 12 + 1):
		balance = balance * (1 + monthly_return) + monthly_saving
		if month % 12 == 0:
			yearly_totals.append({"Year": month // 12, "Total (Rp)": balance})

	return balance, pd.DataFrame(yearly_totals)


st.markdown(
	"""
	<div class="brandbar">
		<div class="brandmark" aria-label="TUMBUH rising chart logo">
			<svg width="30" height="30" viewBox="0 0 30 30" fill="none" aria-hidden="true">
				<path d="M5 23V17M11 23V13M17 23V16M23 23V8" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>
				<path d="m5 13 6-5 5 3 8-7m-5 0h5v5" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
		</div>
		<div>
			<div class="brandname">TUMBUH</div>
			<div class="brandtag">Investment goal calculator</div>
		</div>
	</div>
	""",
	unsafe_allow_html=True,
)

st.session_state.setdefault("ticker_input", "BBCA")
st.session_state.setdefault("company_lookup_done", False)
st.session_state.setdefault("company_overview", None)
st.session_state.setdefault("company_error", None)
st.session_state.setdefault("company_ticker", "BBCA")

with st.form("company_lookup"):
	ticker_input = st.text_input("IDX ticker", key="ticker_input")
	lookup_submitted = st.form_submit_button("Load company")

if lookup_submitted or not st.session_state.company_lookup_done:
	st.session_state.company_ticker = ticker_input.strip().upper()
	try:
		with st.spinner("Loading company details..."):
			st.session_state.company_overview = get_company_overview(
				st.session_state.company_ticker
			)
		st.session_state.company_error = None
	except SectorsError as error:
		st.session_state.company_overview = None
		st.session_state.company_error = str(error)
	st.session_state.company_lookup_done = True

company = st.session_state.company_overview
if st.session_state.company_error:
	st.warning(st.session_state.company_error)
if company:
	st.subheader(company.get("company_name") or st.session_state.company_ticker)
	last_close_price = company.get("last_close_price")
	formatted_price = (
		format_rupiah(float(last_close_price)) if last_close_price is not None else "Unavailable"
	)
	st.markdown(
		f"**Sector:** {company.get('sector') or 'Unavailable'}  \n"
		f"**Sub-sector:** {company.get('sub_sector') or 'Unavailable'}  \n"
		f"**Last close:** {formatted_price}"
	)

st.title("Investment Goal Calculator")
st.write("See how your monthly saving could grow over time.")

monthly_saving = st.number_input(
	"Monthly saving (Rp)", min_value=0, value=1_000_000, step=100_000, format="%d"
)
years = st.number_input("Number of years", min_value=1, max_value=60, value=10, step=1)
yearly_return = st.number_input(
	"Expected yearly return (%)", min_value=-100.0, max_value=100.0, value=8.0, step=0.5
)

final_amount, yearly_totals = project_growth(monthly_saving, years, yearly_return)

st.metric(f"Projected amount after {years} years", format_rupiah(final_amount))
if company:
	try:
		share_price = float(company.get("last_close_price") or 0)
	except (TypeError, ValueError):
		share_price = 0
	if share_price > 0:
		lot_price = share_price * 100
		lots = math.floor(monthly_saving / lot_price)
		leftover = monthly_saving - lots * lot_price
		lot_label = "lot" if lots == 1 else "lots"
		st.markdown(f"Your monthly saving buys **{lots} {lot_label}** of this stock.")
		st.caption(f"Left over: {format_rupiah(leftover)}")
else:
	st.caption("Lot affordability is shown when a valid stock price is available.")

st.subheader("Total by year")
st.line_chart(yearly_totals.set_index("Year"), height=300, color="#E5337E")

st.caption(
	"Estimate only. Actual returns vary. This is not investment advice."
)

with st.expander("Raw company data"):
	if company:
		st.json(company)
	else:
		st.caption("Company data is unavailable until a ticker loads successfully.")
