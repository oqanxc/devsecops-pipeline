
const express = require('express'); // Import the Express framework
const { execFile } = require('child_process'); // Used execFile instead of exec to mitigate command injection risks
const router = express.Router(); // Create an instance of the Express application

function returnInput(input) { // A function that takes user input and returns it without any sanitization or validation
    
    let forwardedInput = input; // The input is directly assigned to a new variable without any checks or modifications
    return forwardedInput;  // The function returns the user input as-is, which can lead to security vulnerabilities if the input is used in sensitive operations
}

router.get('/ping', (req, res) => {
    // 1. SOURCE: user-supplied input is taken from the query parameter 'host'
    let targetHost = req.query.host;
    if (!targetHost) {
        return res.status(400).send("Please provide 'host' parameter: ?host=127.0.0.1");
    }

    let processedHost = returnInput(targetHost); // The user input is passed to the returnInput function, which returns it without any sanitization or validation

    // 2. SINK: The processed input is directly used in a command execution without proper sanitization, leading to potential command injection
    execFile('ping', ['-c', '1', processedHost], (error, stdout, stderr) => {
        if (error) {
            return res.status(500).send(`Error: ${error.message}`);
        }
        res.send(`<pre>${stdout}</pre>`);
    });
});


module.exports = router; // Export the router to be used in other parts of the application