import os
import subprocess
import streamlit as st
import re
from pyvis.network import Network
import pandas as pd
import textwrap

st.set_page_config(page_title="GraphRAG UI Webpage", layout="wide")

if 'working_directory' not in st.session_state:
    st.session_state.working_directory = ''

def filter_query_output(output):
    start_marker = "SUCCESS:"
    try:
        response = output.split(start_marker, 1)[1]
        return f"SUCCESS:{response.strip()}"
    except ValueError:
        return ""

# Fetch names of all projects
def get_project_names():
    projects_path = os.path.join(os.getcwd(), 'projects')
    if os.path.exists(projects_path):
        return sorted([name for name in os.listdir(projects_path) if os.path.isdir(os.path.join(projects_path, name))])
    return []

def display_uploaded_files(input_dir):
    if os.path.exists(input_dir):
        files = os.listdir(input_dir)
        if files:
            st.markdown("##### Uploaded Files")
            for file in files:
                file_path = os.path.join(input_dir, file)
                col_file, col_delete = st.columns([3, 1])
                with col_file:
                    st.write(file)
                with col_delete:
                    if st.button("Delete", key=f"delete_{file}"):
                        try:
                            os.remove(file_path)
                            st.success(f"Deleted {file}")
                        except Exception as e:
                            st.error(f"Error deleting {file}: {e}")
        else:
            st.write("No files uploaded.")
    else:
        st.write("No files uploaded.")

def extract_entities_and_relations(filtered_result):
    entities_pattern = r"Entities\s*\((.*?)\)"
    relationships_pattern = r"Relationships\s*\((.*?)\)"

    entities = []
    relations = []

    # Find all matched "Entities" and "Relationships" data
    entities_matches = re.findall(entities_pattern, filtered_result)
    relationships_matches = re.findall(relationships_pattern, filtered_result)

    # Handle matched Entities
    for match in entities_matches:
        items = match.split(',')
        for item in items:
            item = item.strip()
            if item.startswith('+'):
                break
            try:
                entities.append(int(item))
            except ValueError:
                continue

    # Handle matched Relations
    for match in relationships_matches:
        items = match.split(',')
        for item in items:
            item = item.strip()
            if item.startswith('+'):
                break
            relations.append(item)

    return entities, relations

def generate_cypher_query(entities, relations):
    entities_str = ", ".join(map(str, entities))
    relations_str = ", ".join(f'"{rel}"' for rel in relations)

    cypher_query = f"""
    MATCH (e:__Entity__)
    WHERE e.human_readable_id IN [{entities_str}]
    RETURN e AS source, NULL AS rel, NULL AS target

    UNION

    MATCH (source)-[r:RELATED]->(target)
    WHERE r.human_readable_id IN [{relations_str}]
    RETURN source, r AS rel, target
    """
    return cypher_query

def generate_query_visulization(entities_ids, relations_ids, working_directory):
    GRAPHRAG_FOLDER = os.path.join(working_directory, "output")
    entity_df = pd.read_parquet(
        f"{GRAPHRAG_FOLDER}/create_final_entities.parquet",
        columns=["name", "type", "description", "human_readable_id", "id"]
    )
    rel_df = pd.read_parquet(
        f"{GRAPHRAG_FOLDER}/create_final_relationships.parquet",
        columns=["source", "target", "description", "human_readable_id"]
    )

    filtered_entities = entity_df[entity_df["human_readable_id"].isin(entities_ids)]
    filtered_relations = rel_df[rel_df["human_readable_id"].isin(relations_ids)]

    net = Network(height="750px", width="100%", directed=True)

    # record added nodes
    added_nodes = set()

    for _, row in filtered_entities.iterrows():
        node_id = row['human_readable_id']
        # limit 50 words per line
        description_wrapped = "\n".join(textwrap.wrap(row['description'], width=50))
        net.add_node(
            node_id,
            label=row['name'],  # show name in circle node
            title=f"Name: {row['name']}\nType: {row['type']}\nDescription: {description_wrapped}",  # show info
            group=row['type']
        )
        added_nodes.add(node_id)

    for _, row in filtered_relations.iterrows():
        if row['source'] not in added_nodes:
            net.add_node(row['source'], label=row['source'], title=f"{row['source']}")
            added_nodes.add(row['source'])

        if row['target'] not in added_nodes:
            net.add_node(row['target'], label=row['target'], title=f"{row['target']}")
            added_nodes.add(row['target'])

        description_wrapped = "\n".join(textwrap.wrap(row['description'], width=50))
        net.add_edge(
            row['source'], row['target'],
            title=f"{description_wrapped}",
            # label="relation"
        )

    net.write_html("filtered_graph_visualization.html")

st.title("GraphRAG UI Webpage")

page = st.sidebar.selectbox("Navigate", ["Project Initialization", "Indexing", "Query"])

project_names = get_project_names()
selected_project = st.sidebar.selectbox("Select Project", [""] + project_names)

if selected_project:
    st.session_state.working_directory = os.path.join(os.getcwd(), 'projects', selected_project)
else:
    st.session_state.working_directory = ''

if page == "Project Initialization":
    st.header("Project Initialization")

    project_name = st.text_input("Project Name", placeholder="Please input your project name")

    if st.button("Start Initialization"):
        if project_name:
            projects_dir = os.path.join(os.getcwd(), 'projects')
            project_dir = os.path.join(projects_dir, project_name)

            try:
                if not os.path.exists(projects_dir):
                    os.makedirs(projects_dir)
                    st.info(f"Created directory: {projects_dir}")

                init_command = ["graphrag", "init", "--root", project_dir]
                subprocess.run(init_command, check=True)
                
                st.success("Initialize Project Successfully")

                # update working directory
                st.session_state.working_directory = project_dir

                # clear
                st.session_state['project_name'] = ""

            except subprocess.CalledProcessError as e:
                st.error(f"An error occurred during initialization: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
        else:
            st.warning("Please enter a project name.")

    existing_projects = get_project_names()

    # sidebar
    # st.sidebar.title("GraphRAG UI Webpage")
    # selected_project = st.sidebar.selectbox("Select Project", [""] + existing_projects)

    # if selected_project:
    #     st.session_state.working_directory = os.path.join(os.getcwd(), 'projects', selected_project)

    # Existing Projects Section
    st.subheader("Existing Projects")

    if existing_projects:
        with st.expander("Show Existing Projects"):
            for project in existing_projects:
                st.write(f"- {project}")
    else:
        st.write("No existing projects found.")

elif page == "Indexing":
    # make sure working_directory is selected
    if not st.session_state.working_directory:
        st.warning("Please select a project from the sidebar first.")
        st.stop()

    working_directory = st.session_state.working_directory

    # st.title("GraphRAG UI Webpage")
    # st.header("Indexing")

    # two columns
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("Indexing")
        with st.container():
            # 1. Upload Files
            st.markdown("##### Upload Files (txt files)")
            uploaded_files = st.file_uploader("Upload TXT files", type=["txt"], accept_multiple_files=True)
            if uploaded_files:
                input_dir = os.path.join(working_directory, 'input')
                os.makedirs(input_dir, exist_ok=True)
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(input_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.success(f"Uploaded {len(uploaded_files)} file(s) to {input_dir}")
                display_uploaded_files(input_dir)

            # 2. Language Selection
            st.markdown("##### Language")
            language = st.selectbox("Select Language", ["English", "Chinese"])

            # 3. Chunk Size
            st.markdown("##### Chunk Size")
            chunk_size = st.number_input("Enter Chunk Size (integer)", min_value=1, step=1, value=100)

            # 4. Domain
            st.markdown("##### Domain")
            domain = st.text_input("Enter Domain")

            # # 5. Actions: Prompt Tune and Start Indexing
            # st.markdown("### 5. Actions")
            col_prompt, col_index = st.columns(2)
            with col_prompt:
                if st.button("Prompt Tune"):
                    if not domain:
                        st.warning("Please enter a Domain.")
                    else:
                        try:
                            cmd = [
                                "graphrag", "prompt-tune",
                                "--root", working_directory,
                                "--domain", domain,
                                "--chunk-size", str(chunk_size)
                            ]
                            subprocess.run(cmd, check=True)
                            st.success("Prompt Tuning Success!")
                        except subprocess.CalledProcessError as e:
                            st.error(f"An error occurred during Prompt Tuning: {e}")
                        except Exception as e:
                            st.error(f"Unexpected error: {e}")

            with col_index:
                if st.button("Start Indexing"):
                    try:
                        cmd = [
                            "graphrag", "index",
                            "--root", working_directory
                        ]
                        subprocess.run(cmd, check=True)
                        st.success("Indexing Successfully!")
                    except subprocess.CalledProcessError as e:
                        st.error(f"An error occurred during Indexing: {e}")
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

    with col2:
        st.subheader("Incremental Indexing")
        with st.container():
            # 1. Upload Files
            st.markdown("##### Upload Files (txt files)")
            incremental_files = st.file_uploader("Upload TXT files for Incremental Indexing", type=["txt"], accept_multiple_files=True, key="incremental_upload")
            if incremental_files:
                input_dir = os.path.join(working_directory, 'input')
                os.makedirs(input_dir, exist_ok=True)
                for uploaded_file in incremental_files:
                    file_path = os.path.join(input_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.success(f"Uploaded {len(incremental_files)} file(s) to {input_dir}")

            # # 2. Update Files Button
            # st.markdown("### 2. Actions")
            if st.button("Update Files"):
                try:
                    cmd = [
                        "update",
                        "--root", working_directory
                    ]
                    subprocess.run(cmd, check=True)
                    st.success("Updating Successfully!")
                except subprocess.CalledProcessError as e:
                    st.error(f"An error occurred during Updating: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

elif page == "Query":
    if not st.session_state.working_directory:
        st.warning("Please select a project from the sidebar first.")
        st.stop()

    working_directory = st.session_state.working_directory

    question = st.text_input("Please input your question", placeholder="Enter your question here")

    query_mode = st.selectbox("Query Mode", ["local", "global", "drift"])

    if st.button("Start Query"):
        if question:
            working_directory = st.session_state.working_directory

            query_status = st.info(f"Running query with {query_mode} mode. Please wait...")

            try:
                command = [
                    "graphrag", "query", 
                    "--root", working_directory, 
                    "--method", query_mode, 
                    "--query", question,
                ]
                result = subprocess.run(command, capture_output=True, text=True, check=True)

                filtered_result = filter_query_output(result.stdout)
                enttities, relations = extract_entities_and_relations(filtered_result)
                cypher_query = generate_cypher_query(enttities, relations)

                st.markdown("### Response:")
                with st.expander("Show Response", expanded=True):
                    st.text_area("Query Response", filtered_result, height=600)
                query_status.empty()
                st.success("Response Generated Successfully!")

                generate_query_visulization(enttities, relations, working_directory)
                # display html content
                with open("filtered_graph_visualization.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=750, width=1200, scrolling=True)

                with st.expander("Cypher Query"):
                    st.code(cypher_query, language="cypher")  # automatic copy

            except subprocess.CalledProcessError as e:
                st.error(f"An error occurred: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
        else:
            st.warning("Please input a question before starting the query.")
