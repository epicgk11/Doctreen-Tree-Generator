import streamlit as st
import json
from bson import json_util
from treeGenerator import CombinedMedicalTreeGenerator
from custom2doctreen_parser import CustomToDoctreenConverter
def main():
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
        generator.run(my_bar,my_text)
        st.success("Pipeline completed successfully.")
        st.info("Uploading into doctreen ")
        my_bar.empty()

        owner_id = "679fc806c5dab815f7995fb8"
        
        try:
            with open("combined_tree.json", "r", encoding="utf-8") as infile:
                custom_data = json.load(infile)
            converter = CustomToDoctreenConverter(owner_id, tree_name)
            doctreen_nodes, doctreen_tree, link = converter.convert_custom_to_doctreen(custom_data)
            doctreen_tree['treeNodes'] = doctreen_nodes
            
            with open('Doctreen_Combined_Tree.json', "w", encoding="utf-8") as outfile:
                json_str = json_util.dumps(doctreen_tree, indent=4, ensure_ascii=False)
                outfile.write(json_str)
            
            st.success("Conversion complete!")
            st.write(f"Total nodes inserted: {len(doctreen_nodes)}")
            st.warning(f"Please Log onto doctreen to view the tree",icon="⚠️")
            st.markdown(f"[Link to tree]({link})")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
