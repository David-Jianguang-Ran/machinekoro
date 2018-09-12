import React from "react"

import DiceDisplay from "./diceDisplay"
import EmojiChooser from "./emojiChooser"
import MarketDisplay from "./marketDisplay"
import QueryResponder from "./queryResponder"

class MainUtilityBar extends React.Component{
    /*
    This component has a state change triggered by a ws event listener
    props:
        - ws_manager
        - match_state
        - game_state

    children:
        - Query Responder
        - Market
        - Dice
        - EmojiChooser
        - Menu
    */
    constructor(props){
        super(props)
        this.state = {
            "messages":
        }
    }
    componentDidMount(){
        // register message listener
        // note subsequent attempts to add listener with the same key will overwrite the old listener
        this.props.ws_manager.addMessageListener("action.query",this.handleIncomingQuery)
    }
    handleIncomingQuery(){

    }
    render(){
        return(
            <div>
                <QueryResponder ws_manager={this.props.ws_manager}/>
                <MarketDisplay game_state={this.props.game_state}/>
                <DiceDisplay game_state={this.props.game_state}/>
                <EmojiChooser updateEmojiCallback={this.updateEmojiCallback}/>
            </div>
        )
    }
}