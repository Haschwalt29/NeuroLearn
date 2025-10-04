"""
Content seeder for demo purposes - creates sample learning content
"""

from ..models import Content, db


def seed_sample_content():
    """Create sample learning content for testing"""
    
    sample_content = [
        {
            'topic': 'Python Basics',
            'question': 'What is the correct way to create a list in Python?',
            'answer': 'Use square brackets: my_list = [1, 2, 3] or my_list = []',
            'difficulty': 0.3
        },
        {
            'topic': 'Python Basics',
            'question': 'How do you access the first element of a list?',
            'answer': 'Use index 0: my_list[0]',
            'difficulty': 0.2
        },
        {
            'topic': 'Python Functions',
            'question': 'What keyword is used to define a function in Python?',
            'answer': 'def keyword: def my_function():',
            'difficulty': 0.4
        },
        {
            'topic': 'Python Functions',
            'question': 'How do you return a value from a function?',
            'answer': 'Use the return statement: return value',
            'difficulty': 0.4
        },
        {
            'topic': 'Python Loops',
            'question': 'What is the difference between for and while loops?',
            'answer': 'for loops iterate over a sequence, while loops repeat while a condition is true',
            'difficulty': 0.6
        },
        {
            'topic': 'Python Data Structures',
            'question': 'What is a dictionary in Python?',
            'answer': 'A collection of key-value pairs: my_dict = {"key": "value"}',
            'difficulty': 0.5
        },
        {
            'topic': 'Python Data Structures',
            'question': 'How do you add an item to a dictionary?',
            'answer': 'my_dict["new_key"] = "new_value" or my_dict.update({"key": "value"})',
            'difficulty': 0.5
        },
        {
            'topic': 'Python Classes',
            'question': 'What is the __init__ method used for?',
            'answer': 'It is the constructor method that initializes new instances of a class',
            'difficulty': 0.7
        },
        {
            'topic': 'Python Classes',
            'question': 'How do you create an instance of a class?',
            'answer': 'Call the class like a function: my_instance = MyClass()',
            'difficulty': 0.6
        },
        {
            'topic': 'Python Error Handling',
            'question': 'What is a try-except block used for?',
            'answer': 'To handle exceptions and prevent program crashes',
            'difficulty': 0.7
        },
        {
            'topic': 'Machine Learning',
            'question': 'What is supervised learning?',
            'answer': 'Learning with labeled training data to make predictions on new data',
            'difficulty': 0.8
        },
        {
            'topic': 'Machine Learning',
            'question': 'What is the difference between classification and regression?',
            'answer': 'Classification predicts categories, regression predicts continuous values',
            'difficulty': 0.9
        },
        {
            'topic': 'Machine Learning',
            'question': 'What is overfitting?',
            'answer': 'When a model performs well on training data but poorly on new data',
            'difficulty': 0.9
        },
        {
            'topic': 'Data Analysis',
            'question': 'What is pandas used for?',
            'answer': 'Data manipulation and analysis in Python',
            'difficulty': 0.6
        },
        {
            'topic': 'Data Analysis',
            'question': 'What is a DataFrame?',
            'answer': 'A 2-dimensional labeled data structure with columns and rows',
            'difficulty': 0.7
        }
    ]
    
    # Check if content already exists
    existing_count = Content.query.count()
    if existing_count > 0:
        print(f"Content already exists ({existing_count} items). Skipping seed.")
        return
    
    # Create content
    for item in sample_content:
        content = Content(
            topic=item['topic'],
            question=item['question'],
            answer=item['answer'],
            difficulty=item['difficulty']
        )
        db.session.add(content)
    
    db.session.commit()
    print(f"Created {len(sample_content)} sample content items")


def clear_all_content():
    """Clear all content (for testing)"""
    Content.query.delete()
    db.session.commit()
    print("All content cleared")
