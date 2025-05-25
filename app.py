    missing_cols = [c for c in POSITIONS if c not in existing_df.columns]
    if not missing_cols:
        existing_df = existing_df[POSITIONS]
    st.dataframe(existing_df)

    if not is_admin:
        st.stop()
    else:
        rota_already_exists = True



    # ─────────────────────────────────────────────────────────────
# 🔹 Step 2: Select Inspectors for Each Day
# ─────────────────────────────────────────────────────────────
if not rota_already_exists:
    st.markdown("""
<div style='border:1px solid #ccc; border-radius:10px; padding:1em; background:#f9f9f9; margin-bottom:1.5em;'>
<h4>2️⃣ Select Inspectors for Each Day</h4>
""", unsafe_allow_html=True)
    daily_workers = {}
    daily_heads = {}
    daily_raw_selected = {}
    daily_raw_head = {}

    for i, day in enumerate(days):
        st.markdown(f"🔹 <strong>{day} — { (week_start + timedelta(days=i)).strftime('%d %b %Y') }</strong>", unsafe_allow_html=True)
        cols = st.columns(2)
        with cols[0]:
            selected = st.multiselect(f"Select 6 inspectors for {day}", inspectors, key=day)
        with cols[1]:
            head = st.selectbox(f"Select HEAD for {day}", options=selected if len(selected) == 6 else [], key=day+"_head")
        daily_raw_selected[day] = selected
        daily_raw_head[day] = head
        st.markdown("<div style='margin-bottom: 1em;'></div>", unsafe_allow_html=True)
        if len(set(selected)) == 6 and head in selected:
            daily_workers[day] = [w for w in selected if w != head]
            daily_heads[day] = head

    st.markdown("</div>", unsafe_allow_html=True)

    # Validation
    valid_days = []
    invalid_days = []

    for day in days:
        selected = daily_raw_selected.get(day, [])
        head = daily_raw_head.get(day)
        if len(set(selected)) == 6 and head and head in selected:
            valid_days.append(day)
        elif len(selected) > 0 or head:
            invalid_days.append(day)

    active_days = valid_days
    validation_passed = len(valid_days) > 0 and len(invalid_days) == 0
    if invalid_days:
        st.warning(f"⚠️ Incomplete or invalid selections for: {', '.join(invalid_days)}")

# ─────────────────────────────────────────────────────────────
# 🔹 Step 3: Generate the Weekly Rota
# ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
<div style='border:1px solid #ccc; border-radius:10px; padding:1em; background:#f9f9f9; margin-bottom:1.5em;'>
<h4>3️⃣ Generate the Weekly Rota</h4>
""", unsafe_allow_html=True)

    if validation_passed:
        st.info("✅ Ready to generate rota!")

    if st.button("Generate Rota", disabled=not validation_passed):
        rota_result = generate_rota(
            {day: daily_workers[day] for day in active_days},
            {day: daily_heads[day] for day in active_days},
            rotas, inspectors, week_key
        )
        if isinstance(rota_result, dict) and "error" in rota_result:
            st.error(f"❌ {rota_result['error']}")
            st.stop()
        if not rota_result or not isinstance(rota_result, dict):
            st.error("❌ Rota could not be generated. Please review your selections.")
            st.stop()

        rota_result = {day: roles for day, roles in rota_result.items() if isinstance(roles, dict)}

        for day in days:
            if day not in rota_result:
                rota_result[day] = {
                    "CAR1": "Not Working",
                    "HEAD": "Not Working",
                    "CAR2": "Not Working",
                    "OFFAL": "Not Working",
                    "FCI": "Not Working",
                    "OFFLINE": "Not Working"
                }
        st.success("🎉 Rota saved successfully and added to rota history.")
        

        # Display rota
        
        rota_df = pd.DataFrame.from_dict(rota_result, orient="index")
        rota_df = rota_df.reindex(days)
        missing_columns = [col for col in POSITIONS if col not in rota_df.columns]
        if missing_columns:
            st.warning(f"⚠️ Missing positions in generated rota: {', '.join(missing_columns)}")
        else:
            rota_df = rota_df[POSITIONS]

        st.dataframe(rota_df)
        st.markdown("</div>", unsafe_allow_html=True)

        rota_result = {day: roles for day, roles in rota_result.items() if isinstance(roles, dict)}
        rotas[week_key] = rota_result
        save_rotas(week_key, rota_result)

        
    
