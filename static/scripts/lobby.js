import React from "react"
import ShareBar from "./lobbyComponents"

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
        - ws_manager
        - match_state
     */
    render(){
        return(
            <div className={"full_screen_component"}>
                <ShareBar context={this.props.ws_manager.context}/>
                <LobbyPlayers match_state={this.props.match_state} context={this.props.ws_manager.context}/>
                <LobbyUtilityBar ws_manager={this.props.ws_manager} context={this.props.ws_manager.context}/>
            </div>
        )
    }

}