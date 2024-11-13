# Create Table
```SQL
DROP TABLE IF EXISTS Kanban_Card_Relations;
DROP TABLE IF EXISTS Kanban_Subtasks;
DROP TABLE IF EXISTS Kanban_Cards;
DROP TABLE IF EXISTS Kanban_Card_Types;
DROP TABLE IF EXISTS Kanban_Columns;
DROP TABLE IF EXISTS Kanban_Boards;

CREATE TABLE Kanban_Boards (
    board_id INT PRIMARY KEY IDENTITY(1,1),
    title NVARCHAR(255) NOT NULL,
    description NVARCHAR(MAX)
);

CREATE TABLE Kanban_Columns (
    column_id INT PRIMARY KEY IDENTITY(1,1),
    board_id INT REFERENCES Kanban_Boards(board_id) ON DELETE CASCADE,
    title NVARCHAR(255) NOT NULL,
    position INT
);

CREATE TABLE Kanban_Card_Types (
    card_type_id INT PRIMARY KEY IDENTITY(1,1),
    type NVARCHAR(50) UNIQUE
);

CREATE TABLE Kanban_Cards (
    card_id INT PRIMARY KEY IDENTITY(1,1),
    column_id INT REFERENCES Kanban_Columns(column_id) ON DELETE CASCADE,
    description TEXT,
    card_type_id INT REFERENCES Kanban_Card_Types(card_type_id),
    position INT,
    estimate INT
);

CREATE TABLE Kanban_Subtasks (
    subtask_id INT PRIMARY KEY IDENTITY(1,1),
    parent_card_id INT REFERENCES Kanban_Cards(card_id) ON DELETE CASCADE,
    description TEXT,
    completed BIT NOT NULL DEFAULT 0,
    position INT,
    due_date DATETIME
);

CREATE TABLE Kanban_Card_Relations (
    card_parent_id INT NOT NULL,
    card_child_id INT NOT NULL,
    PRIMARY KEY (card_parent_id, card_child_id),
    FOREIGN KEY (card_parent_id) REFERENCES Kanban_Cards(card_id) ON DELETE NO ACTION,
    FOREIGN KEY (card_child_id) REFERENCES Kanban_Cards(card_id) ON DELETE NO ACTION
);

```