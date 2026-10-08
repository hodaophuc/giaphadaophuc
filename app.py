import streamlit as st
import pandas as pd

# Cấu hình giao diện web
st.set_page_config(
    page_title="Phần Mềm Quản Lý Gia Phả Họ Đào Phúc",
    page_icon="🌳",
    layout="wide"
)

st.title("🌳 PHẦN MỀM QUẢN LÝ GIA PHẢ HỌ ĐÀO PHÚC")
st.markdown("Hệ thống quản lý trực tuyến dòng họ (Hưng Nông – Hùng Tiến – Mỹ Đức – Hà Nội)")
st.markdown("---")

EXCEL_FILE = "Gia_Pha_Ho_Dao_Phuc_Excel_Chuan.xlsx"

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE)
        # Chuẩn hóa tên cột: loại bỏ khoảng trắng thừa để tránh lỗi KeyError
        df.columns = [str(c).strip() for c in df.columns]
        
        string_cols = [
            "Mã thành viên (ID)", "Họ và tên", "Giới tính", "Chi", 
            "Đời", "Mã Cha/Mẹ (Parent ID)", "Tên Cha / Mẹ", 
            "Phu nhân / Phu quân", "Thứ tự / Vai trò", "Ghi chú"
        ]
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str).replace("nan", "")
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file dữ liệu: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- THANH CÔNG CỤ TÌM KIẾM & LỌC (SIDEBAR) ---
    st.sidebar.header("🔍 Tra cứu & Lọc danh sách")
    search_keyword = st.sidebar.text_input("Tìm theo tên hoặc mã ID", "")
    
    # Kiểm tra cột Chi an toàn
    if "Chi" in df.columns:
        chi_options = ["Tất cả"] + sorted([str(x) for x in df["Chi"].unique() if x != ""])
        selected_chi = st.sidebar.selectbox("Lọc theo Chi", chi_options)
    else:
        selected_chi = "Tất cả"
        
    # Kiểm tra cột Đời an toàn
    if "Đời" in df.columns:
        doi_options = ["Tất cả"] + sorted([str(x) for x in df["Đời"].unique() if x != ""])
        selected_doi = st.sidebar.selectbox("Lọc theo Đời", doi_options)
    else:
        selected_doi = "Tất cả"
    
    # Áp dụng bộ lọc
    filtered_df = df.copy()
    if search_keyword:
        filtered_df = filtered_df[
            filtered_df["Họ và tên"].str.lower().str.contains(search_keyword.lower()) |
            filtered_df["Mã thành viên (ID)"].str.lower().str.contains(search_keyword.lower())
        ]
    if selected_chi != "Tất cả" and "Chi" in df.columns:
        filtered_df = filtered_df[filtered_df["Chi"] == selected_chi]
    if selected_doi != "Tất cả" and "Đời" in df.columns:
        filtered_df = filtered_df[filtered_df["Đời"] == selected_doi]
    
    # --- HIỂN THỊ DANH SÁCH THÀNH VIÊN ---
    st.subheader(f"📋 Danh sách thành viên (Hiển thị: {len(filtered_df)} / Tổng số: {len(df)} thành viên)")
    st.dataframe(filtered_df, use_container_width=True, height=350)
    
    st.markdown("---")
    
    # --- TÍNH NĂNG XEM CÂY GIA PHẢ (FAMILY TREE) CỦA THÀNH VIÊN ---
    st.subheader("🌲 Xem Sơ Đồ Cây Gia Phả (Family Tree) Của Thành Viên")
    
    # Tạo danh sách chọn thành viên để xem cây
    member_options = df["Mã thành viên (ID)"].astype(str) + " - " + df["Họ và tên"]
    selected_member_str = st.selectbox("Chọn hoặc tìm tên thành viên để xem nhánh gia phả:", member_options)
    
    if selected_member_str:
        selected_id = selected_member_str.split(" - ")[0]
        current_member = df[df["Mã thành viên (ID)"] == selected_id].iloc[0]
        
        st.markdown(f"### 👤 Thông tin chi tiết: **{current_member['Họ và tên']}** ({current_member['Mã thành viên (ID)']})")
        
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.info(f"**Chi:** {current_member['Chi']}\n\n**Đời:** {current_member['Đời']}")
        with col_t2:
            st.success(f"**Cha / Mẹ:** {current_member['Tên Cha / Mẹ']} (Mã: {current_member['Mã Cha/Mẹ (Parent ID)']})")
        with col_t3:
            st.warning(f"**Phu nhân / Phu quân:** {current_member['Phu nhân / Phu quân']}\n\n**Vai trò:** {current_member['Thứ tự / Vai trò']}")
        
        if current_member['Ghi chú']:
            st.write(f"📝 **Ghi chú:** {current_member['Ghi chú']}")
            
        st.markdown("#### 🌿 Nhánh gia phả liên quan (Tổ tiên & Con cháu):")
        
        # 1. Tìm Cha/Mẹ (Tổ tiên trực hệ phía trên)
        parent_id = current_member['Mã Cha/Mẹ (Parent ID)']
        parent_info = df[df["Mã thành viên (ID)"] == parent_id] if parent_id else pd.DataFrame()
        
        # 2. Tìm anh chị em cùng cha/mẹ
        siblings = pd.DataFrame()
        if parent_id:
            siblings = df[(df["Mã Cha/Mẹ (Parent ID)"] == parent_id) & (df["Mã thành viên (ID)"] != selected_id)]
            
        # 3. Tìm con cháu (Thế hệ tiếp theo phía dưới)
        children = df[df["Mã Cha/Mẹ (Parent ID)"] == selected_id]
        
        tree_col1, tree_col2, tree_col3 = st.columns(3)
        
        with tree_col1:
            st.markdown("⬆️ **Cha / Mẹ (Thân phụ/Thân mẫu):**")
            if not parent_info.empty:
                p = parent_info.iloc[0]
                st.code(f"[{p['Mã thành viên (ID)']}] {p['Họ và tên']} ({p['Đời']})")
            else:
                st.caption("Không có thông tin hoặc là Thủy tổ.")
                
        with tree_col2:
            st.markdown("↔️ **Anh / Chị / Em ruột:**")
            if not siblings.empty:
                for _, s in siblings.iterrows():
                    st.text(f"• [{s['Mã thành viên (ID)']}] {s['Họ và tên']} ({s['Thứ tự / Vai trò']})")
            else:
                st.caption("Không có hoặc chưa cập nhật.")
                
        with tree_col3:
            st.markdown("⬇️ **Con cháu trực hệ:**")
            if not children.empty:
                for _, c in children.iterrows():
                    st.success(f"[{c['Mã thành viên (ID)']}] {c['Họ và tên']} ({c['Thứ tự / Vai trò']})")
            else:
                st.caption("Chưa có thông tin con cháu.")

    st.markdown("---")
    
    # --- CHỨC NĂNG THÊM & SỬA THÀNH VIÊN ---
    tab1, tab2 = st.tabs(["➕ Thêm thành viên mới", "✏️ Chỉnh sửa thông tin thành viên"])
    
    with tab1:
        st.subheader("Thêm con cháu mới vào gia phả (Ví dụ: Đời 14, 15... liên kết qua Mã Cha/Mẹ)")
        with st.form("add_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_id = st.text_input("Mã thành viên (ID) mới", value="GP-14-001", help="Mã định danh duy nhất")
                new_name = st.text_input("Họ và Tên")
                new_gender = st.selectbox("Giới tính", ["Nam", "Nữ"])
            with c2:
                new_chi = st.selectbox("Chi", ["Chi Giáp", "Chi Ất", "Chi Bính", "Chi Đinh", "Chi Mậu", "Tổ dòng"])
                new_doi = st.text_input("Đời", value="Đời thứ 14")
                new_parent_id = st.text_input("Mã Cha/Mẹ (Parent ID)", value="GP-13-001", help="Nhập Mã ID của cha hoặc mẹ")
            with c3:
                new_parent_name = st.text_input("Tên Cha / Mẹ", value="Đào Đức Huy")
                new_spouse = st.text_input("Phu nhân / Phu quân", value="-")
                new_role = st.text_input("Thứ tự / Vai trò", value="Con trưởng")
            
            new_note = st.text_area("Ghi chú (Năm sinh, sự kiện...)")
            
            if st.form_submit_button("Lưu thành viên mới"):
                if new_id and new_name:
                    if new_id in df["Mã thành viên (ID)"].values:
                        st.error(f"Mã thành viên '{new_id}' đã tồn tại! Vui lòng chọn mã khác.")
                    else:
                        new_row = {
                            "Mã thành viên (ID)": new_id,
                            "Họ và tên": new_name,
                            "Giới tính": new_gender,
                            "Chi": new_chi,
                            "Đời": new_doi,
                            "Mã Cha/Mẹ (Parent ID)": new_parent_id,
                            "Tên Cha / Mẹ": new_parent_name,
                            "Phu nhân / Phu quân": new_spouse,
                            "Thứ tự / Vai trò": new_role,
                            "Ghi chú": new_note
                        }
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        df.to_excel(EXCEL_FILE, index=False)
                        st.success(f"Đã thêm thành công thành viên: {new_name}!")
                        st.rerun()
                else:
                    st.error("Vui lòng điền đủ Mã thành viên và Họ tên!")
                    
    with tab2:
        st.subheader("Chỉnh sửa thông tin thành viên hiện có")
        edit_id = st.selectbox("Chọn Mã thành viên cần sửa", df["Mã thành viên (ID)"].tolist())
        
        if edit_id:
            member = df[df["Mã thành viên (ID)"] == edit_id].iloc[0]
            with st.form("edit_form"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_name = st.text_input("Họ và Tên", value=member["Họ và tên"])
                    e_spouse = st.text_input("Phu nhân / Phu quân", value=member["Phu nhân / Phu quân"])
                with ec2:
                    e_role = st.text_input("Thứ tự / Vai trò", value=member["Thứ tự / Vai trò"])
                    e_note = st.text_area("Ghi chú", value=member["Ghi chú"])
                
                if st.form_submit_button("Cập nhật thay đổi"):
                    df.loc[df["Mã thành viên (ID)"] == edit_id, "Họ và tên"] = e_name
                    df.loc[df["Mã thành viên (ID)"] == edit_id, "Phu nhân / Phu quân"] = e_spouse
                    df.loc[df["Mã thành viên (ID)"] == edit_id, "Thứ tự / Vai trò"] = e_role
                    df.loc[df["Mã thành viên (ID)"] == edit_id, "Ghi chú"] = e_note
                    
                    df.to_excel(EXCEL_FILE, index=False)
                    st.success("Đã cập nhật thành công!")
                    st.rerun()
