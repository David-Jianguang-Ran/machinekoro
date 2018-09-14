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
            "is_prime": false,
            "match_state" : null,
            "game_state" : null,
            "match_id":null
        }
        this.componentDidMount = this.componentDidMount.bind(this)
        this.handleMatchUpdate = this.handleMatchUpdate.bind(this)
        this.handleGameStateUpdate = this.handleGameStateUpdate.bind(this)
        this.handleInitMessage = this.handleInitMessage.bind(this)
    }
    componentDidMount(){
        // and event listener for incoming message over ws connection
        this.props.ws_manager.addMessageListener(
            "match_update",this.handleMatchUpdate)
        this.props.ws_manager.addMessageListener(
            "game_update",this.handleGameStateUpdate)
        this.props.ws_manager.addMessageListener(
            "init_message",this.handleInitMessage)
    }
    handleInitMessage(obj){
        /*
        This method updates the state with the new match_state and then set state
        :param: obj a message object with
            key:"init_message"
            content:"prime register obj" <- aka match_register obj in backend
                - is_prime : bool determines privileges
        */
        this.setState({
            is_prime:obj.content.is_prime,
            match_id:obj.content.match_id
        })
    }
    handleMatchUpdate(obj){
        /*
        This method updates the state with the new match_state and then set state
        :param: obj a message object with
            key:"match_update"
            content:"match_state" <- aka match_register obj in backend
        */
        console.log("saving match_state to MKapp.state")
        console.log(typeof obj.content)
        // i dont know wtf is going on here, sometimes match_state is string, sometimes it is obj?
        let new_m_state = null
        if (typeof obj.content === "string"){
            new_m_state = JSON.parse(obj.content)
        } else {
            new_m_state = obj.content
        }
        this.setState({match_state: new_m_state})

    }
    handleGameStateUpdate(obj){
        /*
        This method updates the state with the new game_state and then set state
        :param: obj a message object with
            key:"match_update"
            content:"game_state" <- aka state obj in backend
        */
        this.setState({game_state:obj.content})
    }
    render(){
        if (this.state.match_state == null){
            return (<LoadingDoodad/>)
        } else if (this.state.game_state == null) {
            return (<Lobby ws_manager={this.props.ws_manager}
                           match_state={this.state.match_state}
                           is_prime={this.state.is_prime}
                           match_id={this.state.match_id}
            />)
        } else {
            return (<Main ws_manager={this.props.ws_manager}
                          match_state={this.state.match_state}
                          game_state={this.state.game_state}
                          is_prime={this.state.is_prime}
            />)
        }
    }
}

export default MKApp