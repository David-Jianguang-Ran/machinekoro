import React from 'react'
import ReactDOM from 'react-dom'

import MKApp from "./app"
import WebSocketManager from "./wsManager"

// this is the entry point of the app
const reactContainer = document.getElementById("react_container");

// initialize a ws manager and pass to top level object
// url will be inserted by template engine in html
let ws_manager = new WebSocketManager(url);


ReactDOM.render(
    <MKApp ws_manager={ws_manager} />,
    reactContainer
);