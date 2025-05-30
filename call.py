import streamlit as st
# import json
# from bson import json_util
from treeGenerator import CombinedMedicalTreeGenerator
from custom2doctreen_parser import CustomToDoctreenConverter
def main():
    doctreen_icon = "https://static.wixstatic.com/media/cb6226_4224827f5f13449ebb1ce7b71abbbc10%7Emv2.png/v1/fill/w_192%2Ch_192%2Clg_1%2Cusm_0.66_1.00_0.01/cb6226_4224827f5f13449ebb1ce7b71abbbc10%7Emv2.png"
    doctreen_logo = "https://static.wixstatic.com/media/cb6226_9226c5ad3a1a48e9abb5adbf8e8eb30a~mv2.png/v1/crop/x_53,y_0,w_1223,h_439/fill/w_291,h_104,fp_0.50_0.50,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Logo%20horizontal%20fond%20blanc.png"
    
    st.set_page_config(page_title="Medical Tree Generator", page_icon=doctreen_icon)
    # tree_tuples = (None,'Email', 'Home phone', 'Mobile phone')
    # option = st.selectbox('Existing AI Generated Trees',tree_tuples)
    
    # if (option):
    #     alreadyLink = f"https://front.interns.doctreen.io/edit/{option}"
    #     st.link_button("Click Here to go selected tree",alreadyLink)
    
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="{doctreen_logo}" width="200">
        </div>
    """, unsafe_allow_html=True)
    st.title("Medical Tree Generator & Converter")
    file_type = st.text_input("Enter file type (e.g., 'Thyroid ultrasound')", "Thyroid ultrasound")
    diseases_input = st.text_area("Enter diseases separated by commas", "Nodule Control, Echo Std, Thyroiditis")
    tree_name = st.text_input("Enter tree name", "")
    
    if st.button("Generate & Convert"):
        if not tree_name:
            st.error("Please enter a tree name.")
            return
        
        disease_context = [d.strip() for d in diseases_input.split(",") if d.strip()]
        
        st.info("Generating medical tree...")
        my_bar = st.progress(0,text = "Starting Generation")
        my_text = st.empty()
        generator = CombinedMedicalTreeGenerator(file_type, disease_context)
        tree = generator.run(my_bar,my_text)
        st.success("Pipeline completed successfully.")
        st.info("Uploading into doctreen ")
        my_bar.empty()

        owner_id = "679fc806c5dab815f7995fb8"
        
        try:
            converter = CustomToDoctreenConverter(owner_id, tree_name)
            doctreen_nodes, _, link = converter.convert_custom_to_doctreen(tree)
            
            st.success("Conversion complete!")
            st.write(f"Total nodes inserted: {len(doctreen_nodes)}")
            st.warning(f"Please Log onto doctreen to view the tree",icon="⚠️")
            st.link_button("Click here to go to the generated tree",link)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
