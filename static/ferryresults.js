
// Copyright 2021 Johnathan Pennington | All rights reserved.


let offColor = 'white';
let hoverColor = '#f2f1eb';
let clickedColor = '#e0ded5';

let ferryAlertArray = []; // Each alert is object with keys: container, details.

// Find all ferry alert elements, and add event listeners to them.
for (let ferryAlertNum = 0; ferryAlertNum < 100; ferryAlertNum++) { // Stops after 100 alerts to prevent inf loop.

    let container = document.querySelector('#ferry-alert-' + ferryAlertNum);
    let details = document.querySelector('#ferry-alert-' + ferryAlertNum + ' .ferry-alert-details');

    ferryAlertArray[ferryAlertNum] = { container: container, details: details, };

    if (ferryAlertArray[ferryAlertNum].container === null || ferryAlertArray[ferryAlertNum].details === null) {
        ferryAlertArray.splice(ferryAlertNum, 1); // Deletes the null ferry alert just added.
        break;

    } else {
        ferryAlertArray[ferryAlertNum].container.addEventListener("mouseout", function() { unhoverAlert(ferryAlertNum) });
        ferryAlertArray[ferryAlertNum].container.addEventListener("mouseover", function() { hoverAlert(ferryAlertNum) });
        ferryAlertArray[ferryAlertNum].container.addEventListener("click", function() { clickAlert(ferryAlertNum) });
    };
};


function clickAlert(ferryAlertNum) {

    ferryAlertArray[ferryAlertNum].details.style.display = 'block';
    ferryAlertArray[ferryAlertNum].container.style.backgroundColor = clickedColor;

    // Adjust styling for all alerts that were not the clicked alert.
    for (let alertNum = 0; alertNum < ferryAlertArray.length; alertNum++) {

        if (alertNum === ferryAlertNum) { continue; }; // Skip clicked alert.

        ferryAlertArray[alertNum].details.style.display = 'none';
        ferryAlertArray[alertNum].container.style.backgroundColor = offColor;
    };
};

function hoverAlert(ferryAlertNum) {

    if (ferryAlertArray[ferryAlertNum].details.style.display === 'none') {
        ferryAlertArray[ferryAlertNum].container.style.backgroundColor = hoverColor;
    };
};

function unhoverAlert(ferryAlertNum) {

    if (ferryAlertArray[ferryAlertNum].details.style.display === 'none') {
        ferryAlertArray[ferryAlertNum].container.style.backgroundColor = offColor;
    };
};
