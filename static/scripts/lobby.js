import React from "react"

import LobbyPlayerList from "./lobbyPlayerList"
import LobbyUtilityBar from "./lobbyUtilityBar"
import ShareBar from "./shareBar"

class Lobby extends React.Component{
    /*
    This component is rendered when the game_phase is lobby.
    * Children Component
        - share bar
            props: context (client side equivalent to PlayerConsumer.register  )
        - player list
            props: match_state
        - lobby utility bar
    * props:
        - is_prime
        - ws_manager
        - match_state
        - match_id
     */
    render(){
        return(
            <div className={"full_screen_component"}>
                <ShareBar match_id={this.props.match_id}/>
                <LobbyPlayerList match_state={this.props.match_state} is_prime={this.props.is_prime}/>
                <LobbyUtilityBar ws_manager={this.props.ws_manager} is_prime={this.props.is_prime}/>
            </div>
        )
    }

}

export default Lobby