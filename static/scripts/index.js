import React from 'react'
import ReactDOM from 'react-dom'

import WebSocketManager from "./wsManager"
import DataManager from "./dataManager"

//import App from "./app"
import TestApp from "./testApp"

// this is the entry point of the app
const reactContainer = document.getElementById("react_container");

// initialize a ws manager and pass to top level object
// url will be inserted by template engine in html
let wsManager = new WebSocketManager(url);

// init a data manager obj for passing info from child components to parent
let dataManager = new DataManager();

ReactDOM.render(
    <MKApp wsManager={wsManager} dataManager={dataManager}/>,
    reactContainer
);