"""
نظام المصادقة والصلاحيات
"""
import hashlib
import time
import streamlit as st

def hash_password(password: str) -> str:
    """تجزئة كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    """التحقق من كلمة المرور"""
    return hash_password(password) == stored_hash

def check_admin(password: str) -> bool:
    """التحقق من صلاحية المدير"""
    from config import ADMIN_PASSWORD
    return password == ADMIN_PASSWORD

def check_editor(password: str) -> bool:
    """التحقق من صلاحية المحرر"""
    from config import EDITOR_PASSWORD
    return password == EDITOR_PASSWORD

def require_auth():
    """طلب كلمة المرور للدخول إلى لوحة الإدارة"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.auth_time = 0
        st.session_state.role = None
    
    # التحقق من مهلة الجلسة
    if st.session_state.authenticated:
        if time.time() - st.session_state.auth_time > 3600:
            st.session_state.authenticated = False
            st.warning("انتهت الجلسة، الرجاء تسجيل الدخول مجددًا")
    
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.form("login_form"):
                st.markdown("## 🔐 تسجيل الدخول للوحة الإدارة")
                password = st.text_input("كلمة المرور", type="password")
                role = st.radio("الصلاحية", ["مدير", "محرر"], horizontal=True)
                submitted = st.form_submit_button("دخول", use_container_width=True)
                
                if submitted:
                    if role == "مدير" and check_admin(password):
                        st.session_state.authenticated = True
                        st.session_state.auth_time = time.time()
                        st.session_state.role = "admin"
                        st.success("تم الدخول بنجاح كمدير")
                        st.rerun()
                    elif role == "محرر" and check_editor(password):
                        st.session_state.authenticated = True
                        st.session_state.auth_time = time.time()
                        st.session_state.role = "editor"
                        st.success("تم الدخول بنجاح كمحرر")
                        st.rerun()
                    else:
                        st.error("كلمة المرور غير صحيحة أو الصلاحية غير مناسبة")
        st.stop()
