#!/usr/bin/env python3
"""
Test script for the two core features:
1. PDF to Database Converter
2. Conversational Agent

This script tests the basic functionality without requiring
a live Neo4j database connection.
"""

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing Module Imports")
    print("=" * 40)
    
    try:
        from utils.pdf_processor import PDFProcessor
        print("✅ PDFProcessor imported successfully")
    except ImportError as e:
        print(f"❌ PDFProcessor import failed: {e}")
        return False
    
    try:
        from llm.conversational_agent import ConversationalAgent
        print("✅ ConversationalAgent imported successfully")
    except ImportError as e:
        print(f"❌ ConversationalAgent import failed: {e}")
        return False
    
    try:
        from db.neo4j_client import save_pdf_document_to_neo4j, get_pdf_documents
        print("✅ Neo4j client functions imported successfully")
    except ImportError as e:
        print(f"❌ Neo4j client import failed: {e}")
        return False
    
    print("✅ All imports successful!")
    return True

def test_pdf_processor():
    """Test PDFProcessor functionality"""
    print("\n🧪 Testing PDFProcessor")
    print("=" * 40)
    
    try:
        from utils.pdf_processor import PDFProcessor
        
        # Test instantiation
        processor = PDFProcessor()
        print("✅ PDFProcessor instantiated successfully")
        
        # Test key information extraction
        sample_text = """
        DOCUMENT TITLE: Test Report
        AUTHOR: Test User
        DATE: 2024-01-01
        
        INTRODUCTION:
        This is a test document for validation purposes.
        
        KEY POINTS:
        - Point 1: Important information
        - Point 2: Critical data
        - Point 3: Essential details
        
        TECHNICAL SPECS:
        - Version: 1.0
        - Status: Active
        - Priority: High
        
        CONCLUSION:
        Test completed successfully.
        """
        
        key_info = processor.extract_key_information(sample_text)
        
        # Verify expected keys exist
        expected_keys = ['document_type', 'estimated_word_count', 'has_tables', 
                        'has_numbers', 'language', 'main_topics', 'key_phrases']
        
        for key in expected_keys:
            if key in key_info:
                print(f"✅ {key}: {key_info[key]}")
            else:
                print(f"❌ Missing key: {key}")
                return False
        
        print("✅ PDFProcessor tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ PDFProcessor test failed: {e}")
        return False

def test_conversational_agent():
    """Test ConversationalAgent functionality"""
    print("\n🧪 Testing ConversationalAgent")
    print("=" * 40)
    
    try:
        from llm.conversational_agent import ConversationalAgent
        
        # Test instantiation
        agent = ConversationalAgent()
        print("✅ ConversationalAgent instantiated successfully")
        
        # Test message addition
        agent.add_message("user", "Hello, this is a test message")
        agent.add_message("assistant", "Hello! I'm here to help with your test.")
        
        if len(agent.conversation_history) == 2:
            print("✅ Messages added successfully")
        else:
            print(f"❌ Expected 2 messages, got {len(agent.conversation_history)}")
            return False
        
        # Test context summary
        context = agent.get_context_summary()
        if context and len(context) > 0:
            print("✅ Context summary generated")
        else:
            print("❌ Context summary failed")
            return False
        
        # Test conversation summary
        summary = agent.get_conversation_summary()
        if summary and len(summary) > 0:
            print("✅ Conversation summary generated")
        else:
            print("❌ Conversation summary failed")
            return False
        
        # Test clear history
        agent.clear_history()
        if len(agent.conversation_history) == 0:
            print("✅ History cleared successfully")
        else:
            print("❌ History clear failed")
            return False
        
        print("✅ ConversationalAgent tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ConversationalAgent test failed: {e}")
        return False

def test_neo4j_functions():
    """Test Neo4j client function imports"""
    print("\n🧪 Testing Neo4j Client Functions")
    print("=" * 40)
    
    try:
        from db.neo4j_client import save_pdf_document_to_neo4j, get_pdf_documents
        
        # Check if functions are callable
        if callable(save_pdf_document_to_neo4j):
            print("✅ save_pdf_document_to_neo4j is callable")
        else:
            print("❌ save_pdf_document_to_neo4j is not callable")
            return False
        
        if callable(get_pdf_documents):
            print("✅ get_pdf_documents is callable")
        else:
            print("❌ get_pdf_documents is not callable")
            return False
        
        print("⚠️  Note: Full function testing requires a live Neo4j database connection")
        print("✅ Neo4j client function tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Neo4j client test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 PDF to DB Converter with Conversational Agent - Feature Tests")
    print("=" * 70)
    print()
    
    tests = [
        ("Module Imports", test_imports),
        ("PDFProcessor", test_pdf_processor),
        ("ConversationalAgent", test_conversational_agent),
        ("Neo4j Client", test_neo4j_functions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name} tests...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The core features are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    print("\n📋 Next steps:")
    print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
    print("2. Set up your .env file with required credentials")
    print("3. Run the demo: python demo_features.py")
    print("4. Start the app: streamlit run app.py")

if __name__ == "__main__":
    main() 