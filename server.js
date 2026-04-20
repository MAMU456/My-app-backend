const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const mysql = require('mysql2');

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json()); // Parse JSON request bodies

// Connect to MySQL Database on XAMPP
const db = mysql.createConnection({
  host: 'localhost',        // Host name (localhost for XAMPP)
  user: 'root',             // Default MySQL user for XAMPP
  password: '',             // Default password (usually empty for XAMPP)
  database: 'crud',   // Name of your database
});

db.connect((err) => {
  if (err) {
    console.error('Error connecting to the database:', err);
    return;
  }
  console.log('Connected to the MySQL database.');
});

// Root route
app.get('/', (req, res) => {
  res.send('Welcome to the Students API!');
});

// Get all students
app.get('/api/students', (req, res) => {
  const sql = 'SELECT * FROM students';
  db.query(sql, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).send('Error retrieving students');
    } else {
      res.json(results);
    }
  });
});

// Other routes remain unchanged...
