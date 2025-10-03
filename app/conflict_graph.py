import networkx as nx
import pandas as pd

def build_conflict_graph(enrollments_df):
    """
    Build conflict graph where nodes are courses and edges connect courses 
    that share at least one student (cannot be scheduled at same time).
    
    Args:
        enrollments_df: DataFrame with columns ['student_id', 'course_id']
    
    Returns:
        networkx.Graph: Conflict graph
    """
    G = nx.Graph()
    
    # Debug: Check enrollments DataFrame
    print(f"DEBUG: Enrollments DataFrame shape: {enrollments_df.shape}")
    print(f"DEBUG: Enrollments columns: {list(enrollments_df.columns)}")
    if len(enrollments_df) > 0:
        print(f"DEBUG: First few enrollments:\n{enrollments_df.head()}")
    else:
        print("DEBUG: Enrollments DataFrame is empty!")
        return G
    
    # Check if required columns exist
    if 'course_id' not in enrollments_df.columns:
        raise ValueError(f"Missing 'course_id' column in enrollments DataFrame. Available columns: {list(enrollments_df.columns)}")
    if 'student_id' not in enrollments_df.columns:
        raise ValueError(f"Missing 'student_id' column in enrollments DataFrame. Available columns: {list(enrollments_df.columns)}")
    
    # Get all unique courses
    courses = enrollments_df['course_id'].unique()
    print(f"DEBUG: Found {len(courses)} unique courses: {courses}")
    G.add_nodes_from(courses)
    
    # Group enrollments by student to find conflicts
    student_courses = enrollments_df.groupby('student_id')['course_id'].apply(list).to_dict()
    print(f"DEBUG: Student-course mapping: {dict(list(student_courses.items())[:3])}...")  # Show first 3
    
    # Add edges between courses that share students
    edges_added = 0
    for student_id, course_list in student_courses.items():
        # Add edge between every pair of courses for this student
        for i in range(len(course_list)):
            for j in range(i + 1, len(course_list)):
                course1, course2 = course_list[i], course_list[j]
                if not G.has_edge(course1, course2):
                    G.add_edge(course1, course2)
                    edges_added += 1
    
    print(f"DEBUG: Added {edges_added} conflict edges to graph")
    return G

def graph_stats(G):
    """
    Calculate statistics for the conflict graph.
    
    Args:
        G: networkx.Graph
    
    Returns:
        dict: Graph statistics
    """
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    
    if n_nodes == 0:
        return {
            'n_nodes': 0,
            'n_edges': 0,
            'density': 0.0,
            'avg_degree': 0.0,
            'max_degree_course': None
        }
    
    density = nx.density(G)
    degrees = dict(G.degree())
    avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0.0
    
    max_degree_course = max(degrees, key=degrees.get) if degrees else None
    
    return {
        'n_nodes': n_nodes,
        'n_edges': n_edges,
        'density': density,
        'avg_degree': avg_degree,
        'max_degree_course': max_degree_course
    }

if __name__ == "__main__":
    # Demo with sample data
    sample_enrollments = pd.DataFrame([
        {'student_id': 'S001', 'course_id': 'C001'},
        {'student_id': 'S001', 'course_id': 'C002'},
        {'student_id': 'S002', 'course_id': 'C002'},
        {'student_id': 'S002', 'course_id': 'C003'},
        {'student_id': 'S003', 'course_id': 'C001'},
        {'student_id': 'S003', 'course_id': 'C003'},
    ])
    
    print("Sample enrollments:")
    print(sample_enrollments)
    print()
    
    G = build_conflict_graph(sample_enrollments)
    stats = graph_stats(G)
    
    print("Conflict graph statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print(f"\nEdges (conflicts): {list(G.edges())}")