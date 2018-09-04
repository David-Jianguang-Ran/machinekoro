import React from 'react'

import Lobby from './lobby'
import Main from './main'
import LoadingDoodad from "./loadingDoodad"

class MKApp extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            "game_phase" : this.props.dataManager.storage['game_phase']
        }
        this.component_roster = {
            "loading" : (
                <LoadingDoodad/>
            ),
            "lobby" : (
                <Lobby/>
            ),
            "main" : (
                <Main/>
            )
        }
        this.componentDidMount = this.componentDidMount.bind(this)
        this.handleRegisterUpdate = this.handleRegisterUpdate.bind(this)
    }
    componentDidMount(){
        // and event listener for incoming message over ws connection
        this.props.wsManager.addMessageListener(
            "register_update",this.handleRegisterUpdate())
        this.props.wsManager.addMessageListener(
            "world_update",this.handleWorldStateUpdate())
    }
    handleRegisterUpdate(obj){
        // copy match register obj to data storage
        this.props.dataManager.writeToStorage("match_register",obj)
        // set game phase to lobby if it was loading
        if (this.props.dataManager.storage['game_phase'] != "loading"){
            this.props.dataManager.writeToStorage("game_phase","lobby")
        }
    }
    handleWorldStateUpdate(obj){
        // copy match register obj to data storage set game phase to
        this.props.dataManager.writeToStorage("state",obj)
        if (this.props.dataManager.storage['game_phase'] != "main"){
            this.props.dataManager.writeToStorage("game_phase","main")
        }

    }

    render(){
        return this.component_roster[this.state["game_phase"]]
    }
}

export default App