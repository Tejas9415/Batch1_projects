"""
app.py
------
Streamlit frontend - Graph 1 (Interview Prep + Mock Loop) aur Graph 2
(Resume Editor) dono ko ek UI mein wire karta hai.

Run: streamlit run app.py
"""

import uuid                                                                 # unique thread_id generate karne ke liye (Python ki built-in library)

import streamlit as st                                                     # Streamlit ka main import
from langgraph.types import Command                                        # interrupt() ke baad resume karne ke liye chahiye

from core.graph import build_graph                                         # Graph 1 ki factory function (Day 3, Segment A6)
from core.resume_editor_graph import build_resume_editor_graph             # Graph 2 ki factory function (aaj ka Segment A4)

st.set_page_config(page_title="Interview Prep Coach", layout="wide")       # browser tab ka title aur wide layout set kiya


@st.cache_resource                                                          # Streamlit decorator - is function ka result CACHE ho jaata hai, poore app-lifetime mein sirf EK BAAR chalega
def get_graph1():                                                           # Graph 1 ko baar-baar rebuild karna wasteful hai (checkpointer connection dobara-dobara khulega)
    return build_graph()                                                   # compiled Graph 1 return karta hai


@st.cache_resource                                                          # same reasoning Graph 2 ke liye
def get_graph2():
    return build_resume_editor_graph()                                     # compiled Graph 2 return karta hai


graph1 = get_graph1()                                                       # cached Graph 1 instance liya
graph2 = get_graph2()                                                       # cached Graph 2 instance liya

if "thread_id" not in st.session_state:                                    # session_state mein pehli baar check - yeh naya browser session hai kya?
    st.session_state.thread_id = str(uuid.uuid4())                         # naya unique thread_id banaya - yehi Graph 1 ke checkpointer ki "session identity" hai
if "phase" not in st.session_state:                                        # "phase" batata hai UI abhi kis stage mein hai
    st.session_state.phase = "input"                                       # shuruaat mein "input" phase - abhi form dikhega
if "graph1_result" not in st.session_state:                                # graph1 ka latest result yahan store hoga
    st.session_state.graph1_result = None                                  # abhi tak kuch nahi
if "graph2_result" not in st.session_state:                                # graph2 ka latest result yahan store hoga
    st.session_state.graph2_result = None                                  # abhi tak kuch nahi

st.title("🎯 Interview Prep Coach")                                        # page ka main heading

tab1, tab2 = st.tabs(["📋 Interview Prep + Mock Loop", "📄 Resume Editor"])  # do tabs banaye - dono graphs alag-alag jagah


# ======================= TAB 1: GRAPH 1 =======================
with tab1:                                                                  # is block ke andar jo bhi hoga, Tab 1 mein dikhega

    if st.session_state.phase == "input":                                  # sirf "input" phase mein form dikhao
        st.subheader("Step 1: Apni details do")                            # sub-heading
        mode = st.radio("Mode chuno:", ["new_prep", "debrief"])            # radio button - dono modes mein se ek chunna hai (Day 2 ka mode-branching yahan use hota hai)

        with st.form("input_form"):                                        # st.form - saare inputs ek saath submit honge, har keystroke par rerun nahi hoga (performance)
            company_name = st.text_input("Company Name")                   # company ka naam
            role_title = st.text_input("Role Title")                       # role ka naam

            if mode == "new_prep":                                         # agar new_prep mode chuna hai
                resume_text = st.text_area("Resume Text", height=150)      # resume paste karne ke liye text area
                jd_text = st.text_area("Job Description", height=150)      # JD paste karne ke liye text area
                round_name = what_went_well = what_went_wrong = difficulty_faced = ""  # debrief ke fields khali rakhe (is mode mein zaroorat nahi)
            else:                                                          # mode == "debrief"
                resume_text = jd_text = ""                                 # new_prep ke fields khali rakhe
                round_name = st.text_input("Round Name (e.g. Technical Round 1)")  # kaunsa round tha
                what_went_well = st.text_area("Kya achha gaya?")           # student ka self-report
                what_went_wrong = st.text_area("Kya struggle hua?")        # student ka self-report
                difficulty_faced = st.text_area("Specific difficulty (optional)")  # optional detail

            submitted = st.form_submit_button("Start")                     # submit button - dabane par form ka data lock ho jaata hai

        if submitted:                                                      # agar abhi form submit hua hai
            initial_input = {                                              # Graph 1 ko jaane wala initial state dict banaya
                "mode": mode,                                               # chuna hua mode
                "company_name": company_name,                              # company naam
                "role_title": role_title,                                  # role naam
                "resume_text": resume_text,                                 # resume (agar new_prep hai, warna khali)
                "jd_text": jd_text,                                        # JD (agar new_prep hai, warna khali)
                "round_name": round_name,                                  # round naam (agar debrief hai, warna khali)
                "what_went_well": what_went_well,                          # (agar debrief hai)
                "what_went_wrong": what_went_wrong,                        # (agar debrief hai)
                "difficulty_faced": difficulty_faced,                      # (agar debrief hai)
            }
            config = {"configurable": {"thread_id": st.session_state.thread_id}}  # is session ka thread_id - checkpointer isse state save/resume karega
            with st.spinner("Analysis + prep package + company research chal raha hai..."):  # loading spinner - kyunki LLM calls time lete hain
                result = graph1.invoke(initial_input, config=config)       # GRAPH 1 CHALAO - yeh line collect_answers tak chalegi aur wahin ruk jaayegi (interrupt)
            st.session_state.graph1_result = result                       # result ko session_state mein save kiya (persist karne ke liye)
            st.session_state.phase = "interrupted" if "__interrupt__" in result else "done"  # check karo graph ruka ya poora chal gaya
            st.rerun()                                                     # Streamlit ko force kiya turant rerun karne - taaki naya phase turant reflect ho

    if st.session_state.phase == "interrupted":                            # agar graph interrupt() par ruka hua hai
        st.subheader("Step 2: Mock Interview Questions")                   # sub-heading
        interrupt_payload = st.session_state.graph1_result["__interrupt__"][0].value  # interrupt() ne jo dict bheja tha (Day 3, collect_answers.py), woh yahan milta hai
        st.info(interrupt_payload["instructions"])                          # instruction text dikhao ("In sawalon ke jawab do:")

        with st.form("answers_form"):                                      # naya form - answers collect karne ke liye
            answers = {}                                                   # empty dict - har question ka jawab yahan bharenge
            for q in interrupt_payload["questions"]:                       # interrupt payload ke har question ke liye
                answers[q["id"]] = st.text_area(f"[{q['category']}] {q['text']}", key=q["id"])  # ek text_area banaya - key=q["id"] zaroori hai taaki Streamlit har widget ko unique treat kare
            resume_submitted = st.form_submit_button("Submit Answers")     # submit button

        if resume_submitted:                                               # agar answers submit hue
            config = {"configurable": {"thread_id": st.session_state.thread_id}}  # SAME thread_id - warna checkpointer ko pata nahi chalega yeh kaunsa session resume ho raha hai
            with st.spinner("Answers evaluate ho rahe hain..."):           # loading spinner
                result = graph1.invoke(
    Command(resume={"answers": answers}),
    config=config
)  # GRAPH KO RESUME KARO - answers dict wahi value ban jaayegi jo interrupt() ne "return" ki thi
            st.session_state.graph1_result = result                       # naya result save kiya
            st.session_state.phase = "interrupted" if "__interrupt__" in result else "done"  # phir check karo - agar retry loop trigger hua, phase phir "interrupted" hi rahega
            st.rerun()                                                     # rerun taaki naya phase turant dikhe (agar retry hua toh naye weak questions ka form aayega)

    if st.session_state.phase == "done":                                   # agar graph poora complete ho chuka hai (compile_report tak pahunch gaya)
        st.subheader("✅ Final Report")                                    # sub-heading
        st.markdown(st.session_state.graph1_result["final_report"])       # final_report field ko markdown ke roop mein render kiya (LLM ne markdown format mein hi likha tha)

        if st.button("🔄 Naya session shuru karo"):                        # naya session start karne ka button (naya student ya naya attempt)
            st.session_state.thread_id = str(uuid.uuid4())                 # naya thread_id - purana session poora alag rahega checkpointer mein
            st.session_state.phase = "input"                               # phase wapas "input" par
            st.session_state.graph1_result = None                          # purana result clear kiya
            st.rerun()                                                     # rerun taaki form phir se dikhe


# ======================= TAB 2: GRAPH 2 =======================
with tab2:                                                                  # is block ke andar jo bhi hoga, Tab 2 mein dikhega
    st.subheader("Resume ko is JD ke liye tailor karo")                    # sub-heading

    with st.form("resume_editor_form"):                                   # Graph 2 ke liye alag form (Graph 1 se independent)
        re_company = st.text_input("Company Name", key="re_company")      # key="re_company" zaroori hai taaki Tab 1 ke "company_name" widget se clash na ho
        re_role = st.text_input("Role Title", key="re_role")              # role
        re_resume = st.text_area("Original Resume", height=150, key="re_resume")  # original resume text
        re_jd = st.text_area("Job Description", height=150, key="re_jd")  # JD text
        re_submitted = st.form_submit_button("Tailor Resume")             # submit button

    if re_submitted:                                                       # agar form submit hua
        with st.spinner("Resume score ho raha hai, tailor ho raha hai, dobara score ho raha hai..."):  # spinner - kyunki 3 LLM calls + docx save honge
            result2 = graph2.invoke(                                       # GRAPH 2 CHALAO - yeh EK HI invoke() mein poora pipeline chalta hai (koi interrupt nahi hai isme)
                {
                    "resume_text": re_resume,                              # form se liya
                    "jd_text": re_jd,                                      # form se liya
                    "company_name": re_company,                            # form se liya
                    "role_title": re_role,                                 # form se liya
                }
            )
        st.session_state.graph2_result = result2                          # result save kiya taaki neeche display ho sake, aur agla rerun bhi ise dikha sake

    if st.session_state.graph2_result:                                     # agar koi result available hai (is run mein ya pichle rerun se)
        result2 = st.session_state.graph2_result                          # local variable mein utha liya (readability ke liye)
        col1, col2, col3 = st.columns(3)                                   # 3 columns - side-by-side metrics dikhane ke liye
        with col1:                                                         # pehla column
            st.metric("Original Score", f"{result2['original_match_score']:.0f}/100")  # st.metric - Streamlit ka built-in "big number" widget
        with col2:                                                         # doosra column
            st.metric(                                                     # naya score, aur delta (farak) bhi dikhaya
                "New Score",
                f"{result2['new_match_score']:.0f}/100",
                delta=f"{result2['new_match_score'] - result2['original_match_score']:.0f}",  # delta = kitna improve hua - Streamlit isko green/red arrow ke saath dikhata hai
            )
        with col3:                                                         # teesra column
            with open(result2["tailored_resume_docx_path"], "rb") as f:    # docx file ko binary mode mein khola ("rb" = read bytes)
                st.download_button(                                        # Streamlit ka download button - browser mein file download trigger karta hai
                    "📥 Download Tailored Resume (.docx)",                  # button ka label
                    data=f.read(),                                         # file ka poora binary content
                    file_name="tailored_resume.docx",                      # user ke computer par jis naam se save hoga
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx file ka correct MIME type - iske bina browser file ko sahi se handle nahi karega
                )

        st.subheader("Tailored Resume Preview")                            # sub-heading
        tailored = result2["tailored_resume"]                              # TailoredResume Pydantic object nikala
        st.write("**Professional Summary:**", tailored.professional_summary)  # summary dikhaya
        st.write("**Skills:**", ", ".join(tailored.skills_section))        # skills dikhaye
        st.write("**Experience:**")                                        # experience heading
        for bullet in tailored.experience_bullets:                         # har bullet ke liye loop
            st.write(f"- {bullet}")                                        # bullet point format mein dikhaya