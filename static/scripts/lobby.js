import React from "react"

import LobbyPlayers from "./lobbyPlayerList"
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
     */
    render(){
        return(
            <div className={"full_screen_component"}>
                <ShareBar context={this.props.ws_manager.context}/>
                <LobbyPlayers match_state={this.props.match_state} is_prime={this.props.is_prime}/>
                <LobbyUtilityBar ws_manager={this.props.ws_manager} is_prime={this.props.is_prime}/>
            </div>
        )
    }

}

export default Lobby