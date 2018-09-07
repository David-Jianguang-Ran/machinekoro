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
        - match_state:
        - game_state:

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
        /*
        This method updates the state with the new match_state and then set state
        :param: obj a message object with
            key:"match_update"
            content:"match_state" <- aka match_register obj in backend
        */
        let new_state = {}
        for ( let key in this.state ){
            new_state.key = this.state.key
        }
        new_state.match_state = obj.content

        this.setState({new_state})

    }
    handleGameStateUpdate(obj){
        /*
        This method updates the state with the new game_state and then set state
        :param: obj a message object with
            key:"match_update"
            content:"game_state" <- aka state obj in backend
        */
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