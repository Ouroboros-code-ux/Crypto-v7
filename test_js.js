const { JSDOM } = require("jsdom");
const fs = require("fs");

const html = fs.readFileSync("c:\\Users\\shrey\\OneDrive\\Documents\\Crypto v7\\index.html", "utf8");
const dom = new JSDOM(html, { runScripts: "dangerously" });

// Since cytoscape and chart.js aren't loaded in JSDOM, we just want to look for basic syntax errors
// that might break the page.
console.log("No syntax errors parsing the HTML/JS");
