// n8n Code Node - Parse AI Agent Output and Extract Crash Report JSON
// This node extracts the JSON from the AI response and formats it for the dashboard API

// Get the AI agent's output
const aiOutput = $input.all();

// Initialize result
let reportData = null;
let errorMessage = null;

try {
  // The AI output should be in the chat message
  // n8n chat nodes typically output in this structure
  let fullMessage = '';

  // Try different possible locations for the AI response
  if (aiOutput && aiOutput.length > 0) {
    const item = aiOutput[0];

    // Check common locations where chat output might be
    if (item.json.output) {
      fullMessage = item.json.output;
    } else if (item.json.message) {
      fullMessage = item.json.message;
    } else if (item.json.text) {
      fullMessage = item.json.text;
    } else if (item.json.response) {
      fullMessage = item.json.response;
    } else {
      // If none of the above, stringify the whole json and look for our markers
      fullMessage = JSON.stringify(item.json);
    }
  }

  console.log('Full AI Message:', fullMessage);

  // Extract JSON between markers
  const startMarker = '###JSON_START###';
  const endMarker = '###JSON_END###';

  const startIndex = fullMessage.indexOf(startMarker);
  const endIndex = fullMessage.indexOf(endMarker);

  if (startIndex === -1 || endIndex === -1) {
    throw new Error('JSON markers not found in AI response. The AI may not have generated a final report yet, or the format is incorrect.');
  }

  // Extract the JSON string
  const jsonString = fullMessage.substring(startIndex + startMarker.length, endIndex).trim();

  console.log('Extracted JSON String:', jsonString);

  // Parse the JSON
  reportData = JSON.parse(jsonString);

  // Validate required fields
  if (!reportData.driver) {
    throw new Error('Missing required field: driver');
  }
  if (!reportData.date) {
    throw new Error('Missing required field: date');
  }
  if (!reportData.event) {
    throw new Error('Missing required field: event');
  }

  // Ensure parts is an array
  if (!reportData.parts) {
    reportData.parts = [];
  }

  // Ensure all parts have required fields and correct types
  reportData.parts = reportData.parts.map(part => ({
    part_number: part.part_number || '',
    part: part.part || '',
    likelihood: part.likelihood || 'Possible',
    price: typeof part.price === 'number' ? part.price : (parseFloat(part.price) || 0),
    qty: typeof part.qty === 'number' ? part.qty : (parseInt(part.qty) || 1)
  }));

  // Set default values for optional fields
  if (!reportData.chassis) {
    reportData.chassis = '';
  }
  if (!reportData.accident_damage) {
    reportData.accident_damage = '';
  }

  console.log('Parsed Report Data:', JSON.stringify(reportData, null, 2));

} catch (error) {
  errorMessage = `Error parsing crash report: ${error.message}`;
  console.error(errorMessage);
  console.error('Full error:', error);
}

// Return the result
if (reportData) {
  return [{
    json: {
      success: true,
      reportData: reportData,
      message: 'Crash report parsed successfully'
    }
  }];
} else {
  return [{
    json: {
      success: false,
      error: errorMessage,
      message: 'Failed to parse crash report. Please ensure the AI has generated a complete report with JSON markers.'
    }
  }];
}
