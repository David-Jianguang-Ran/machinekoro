import React from 'react'
import ReactDOM from 'react-dom'

import WebSocketManager from "./dataManager"
//import App from "./app"
import TestApp from "./testApp"

// this is the entry point of the app
const reactContainer = document.getElementById("react_container");

// initialize a ws manager and pass to top level object
// url will be inserted by template engine in html
let wsManager = new WebSocketManager(url);

ReactDOM.render(
    <TestApp wsManager={wsManager}/>,
    reactContainer
);