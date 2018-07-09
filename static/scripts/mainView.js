import React from 'react'
import ReactDOM from 'react-dom'
import { Router , Route } from 'react-router'
import {commonComponent} from './common'
import {lobbyComponent} from './lobby'
import {gameComponent} from './game'
import WebSocketManager from "./dataManager"


const reactContainer = document.getElementById("reactContainer")


class MainView extends React.Component {
    constructor(props){
        super(props)
        this.props.wsManager = new WebSocketManager(this.props.match.param.roomSerial)
    }
    render() {
        return (
            <div className={"mainView"}>
                <Route path={"/lobby/"} component={lobbyComponent}/>
                <Route path={"/game/"} component={gameComponent}/>
                <commonComponent/>
            </div>
        )
    }
}

ReactDOM.render(
    <Router>
       <Route path={"/:roomSerial/"} component={MainView}/>
    </Router>,
    reactContainer
)