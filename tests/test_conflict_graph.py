import pytest
import pandas as pd
import networkx as nx
from app.conflict_graph import build_conflict_graph, graph_stats

def test_build_conflict_graph_basic():
    """Test basic conflict graph construction"""
    
    # Create sample enrollments
    enrollments = pd.DataFrame([
        {'student_id': 'S001', 'course_id': 'C001'},
        {'student_id': 'S001', 'course_id': 'C002'},
        {'student_id': 'S002', 'course_id': 'C002'},
        {'student_id': 'S002', 'course_id': 'C003'},
        {'student_id': 'S003', 'course_id': 'C001'},
        {'student_id': 'S003', 'course_id': 'C003'},
    ])
    
    # Build conflict graph
    G = build_conflict_graph(enrollments)
    
    # Assertions
    assert isinstance(G, nx.Graph)
    assert G.number_of_nodes() == 3  # C001, C002, C003
    
    # Check specific conflicts
    assert G.has_edge('C001', 'C002')  # S001 takes both
    assert G.has_edge('C002', 'C003')  # S002 takes both
    assert G.has_edge('C001', 'C003')  # S003 takes both
    
    # Should be a complete graph (all courses conflict)
    assert G.number_of_edges() == 3

def test_build_conflict_graph_no_conflicts():
    """Test conflict graph with no conflicts"""
    
    # Each student takes only one course
    enrollments = pd.DataFrame([
        {'student_id': 'S001', 'course_id': 'C001'},
        {'student_id': 'S002', 'course_id': 'C002'},
        {'student_id': 'S003', 'course_id': 'C003'},
    ])
    
    G = build_conflict_graph(enrollments)
    
    # Should have nodes but no edges
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 0

def test_graph_stats():
    """Test graph statistics calculation"""
    
    # Create sample enrollments with known conflicts
    enrollments = pd.DataFrame([
        {'student_id': 'S001', 'course_id': 'C001'},
        {'student_id': 'S001', 'course_id': 'C002'},
        {'student_id': 'S002', 'course_id': 'C003'},
    ])
    
    G = build_conflict_graph(enrollments)
    stats = graph_stats(G)
    
    # Assertions
    assert 'n_nodes' in stats
    assert 'n_edges' in stats
    assert 'density' in stats
    assert 'avg_degree' in stats
    assert 'max_degree_course' in stats
    
    assert stats['n_nodes'] == 3
    assert stats['n_edges'] == 1  # Only C001-C002 conflict
    assert stats['density'] == pytest.approx(1/3, rel=1e-2)  # 1 edge out of 3 possible
    assert stats['max_degree_course'] in ['C001', 'C002']  # Both have degree 1

def test_graph_stats_empty():
    """Test graph statistics with empty graph"""
    
    enrollments = pd.DataFrame(columns=['student_id', 'course_id'])
    G = build_conflict_graph(enrollments)
    stats = graph_stats(G)
    
    assert stats['n_nodes'] == 0
    assert stats['n_edges'] == 0
    assert stats['density'] == 0.0
    assert stats['avg_degree'] == 0.0
    assert stats['max_degree_course'] is None

def test_complex_conflict_scenario():
    """Test more complex conflict scenario"""
    
    enrollments = pd.DataFrame([
        {'student_id': 'S001', 'course_id': 'C001'},
        {'student_id': 'S001', 'course_id': 'C002'},
        {'student_id': 'S001', 'course_id': 'C003'},
        {'student_id': 'S002', 'course_id': 'C001'},
        {'student_id': 'S002', 'course_id': 'C004'},
        {'student_id': 'S003', 'course_id': 'C004'},
        {'student_id': 'S003', 'course_id': 'C005'},
    ])
    
    G = build_conflict_graph(enrollments)
    stats = graph_stats(G)
    
    # Expected conflicts:
    # S001: C001-C002, C001-C003, C002-C003
    # S002: C001-C004
    # S003: C004-C005
    
    assert stats['n_nodes'] == 5
    assert stats['n_edges'] == 5
    
    # C001 should have highest degree (connected to C002, C003, C004)
    degrees = dict(G.degree())
    assert degrees['C001'] == 3
    assert stats['max_degree_course'] == 'C001'