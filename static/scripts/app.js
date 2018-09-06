import React from 'react'

import Lobby from './lobby'
import Main from './main'
import LoadingDoodad from "./loadingDoodad"

class MKApp extends React.Component {
    /*
    This is the top level component

    * Children:
    (only one should be rendered at a time)
    -LoadingDoodad
    -Lobby
        props: ws_manager match_state
    -Main
        props: ws_manager match_state game_state

    * States:


    * Props:
    - ws_manager



    */
    constructor(props){
        super(props)
        this.state = {
            "match_state" : null,
            "game_state" : null
        }
        this.componentDidMount = this.componentDidMount.bind(this)
        this.handleMatchUpdate = this.handleMatchUpdate.bind(this)
        this.handleGameStateUpdate = this.handleGameStateUpdate.bind(this)
    }
    componentDidMount(){
        // and event listener for incoming message over ws connection
        this.props.ws_manager.addMessageListener(
            "match_update",this.handleMatchUpdate())
        this.props.ws_manager.addMessageListener(
            "game_update",this.handleGameStateUpdate())
    }
    handleMatchUpdate(obj){
        // update match state with new match register
        let new_state = {}
        for ( let key in this.state ){
            new_state.key = this.state.key
        }
        new_state.match_state = obj.content

        this.setState({new_state})

    }
    handleGameStateUpdate(obj){
        // update game state with new match register
        let new_state = {}
        for ( let key in this.state ){
            new_state.key = this.state.key
        }
        new_state.game_state = obj.content

        this.setState({new_state})

    }
    render(){
        if (this.state.match_state == null){
            return (<LoadingDoodad/>)
        } else if (this.state.game_state == null) {
            return (<Lobby ws_manager={this.props.ws_manager}
                           match_state={this.state.match_state}/>)
        } else {
            return (<Main ws_manager={this.props.ws_manager}
                          match_state={this.state.match_state}
                          game_state={this.state.game_state}/>)
        }
    }
}

export default MKApp