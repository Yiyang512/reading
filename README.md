# French Reading Practice Tool

A comprehensive web application for French reading practice specifically designed for TEF and DELF exam preparation. This tool helps users improve their French reading comprehension skills with timed practice exercises across multiple proficiency levels.

## Features

- Multiple French reading passages organized by CEFR levels (A1, A2, B1, B2)
- Various question types (multiple choice, checkbox, short answer)
- 10-minute countdown timer to simulate real exam conditions
- Immediate feedback on answers
- Correct answer highlighting and explanations
- Level selection interface
- Multiple texts per level
- Clean, responsive design for mobile and desktop

## Getting Started

1. Open `index.html` in your web browser
2. Select your proficiency level (A1, A2, B1, or B2)
3. Choose a reading passage from the dropdown menu
4. Start the timer when you're ready to begin
5. Read the passage and answer the comprehension questions
6. Click "Vérifier mes réponses" to submit and see your score
7. Review the feedback for each question
8. Click "Voir les réponses" to see all correct answers with highlighted text in the passage

## Structure

The application is organized with the following files:

- `index.html`: Main HTML structure
- `css/styles.css`: Responsive styling
- `js/data.js`: Contains all reading passages and questions
- `js/script.js`: Handles the application logic, including level selection, timers, and scoring

## Adding More Content

To add more reading passages:

1. Open `js/data.js`
2. Add a new reading object to the appropriate level array
3. Each reading should include:
   - A unique ID
   - A title
   - HTML content for the reading passage
   - An array of questions with appropriate options and correct answers

## Technologies Used

- HTML5
- CSS3 (with responsive design)
- Vanilla JavaScript (no frameworks)

## Future Improvements

- Additional passages for each level (targeting 20+ per level)
- Progress tracking
- User accounts to save progress
- Exam-specific practice modes (TEF vs DELF)
- Printable PDF versions
- Advanced statistics on user performance

## License

This project is open source and available for personal and educational use. 