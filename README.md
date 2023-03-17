# Todo List Python Application

This is a simple Todo List application written in Python using the PySide6 library. The application allows you to add, edit, and remove tasks, as well as filter and sort them based on various criteria.

![Todo List App Screenshot](./screenshot.png)

## Features

- Add tasks with a title, description, start date, end date, and an optional urgency flag
- Edit existing tasks
- Remove tasks from the To-Do or Done lists
- Double-click tasks in the To-Do list to mark them as done
- Filter tasks by upcoming due dates
- Sort tasks by start date or end date

## Installation

Before running the application, make sure to install the required dependencies. You can do this by running the following command:

```bash
pip install -r requirements.txt
```


## Running the Application

To run the application, simply execute the `main.py` file:

```bash
python main.py
```


## Application Structure

The project is organized as follows:

- `main.py`: This is the entry point of the application. It initializes and runs the main window.
- `todo_list.py`: This file contains the `TodoApp` class, which handles the application logic and user interface.
- `requirements.txt`: This file lists the required Python packages for the application.

## Contributing

If you'd like to contribute to this project, please feel free to submit a pull request or open an issue on GitHub.

## License

This project is released under the MIT License. See the [LICENSE](./LICENSE) file for details.
