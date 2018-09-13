import React from "react"

import DiceDisplay from "./diceDisplay"
import EmojiChooser from "./emojiChooser"
import MarketDisplay from "./marketDisplay"
import QueryResponder from "./queryResponder"
import UtilityMenu from "./utilityMenu"

class MainUtilityBar extends React.Component{
    /*
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
    }
    updateEmojiCallback(){

    }
    render(){
        return(
            <div className={"utility_bar"}>
                <QueryResponder ws_manager={this.props.ws_manager}/>
                <MarketDisplay game_state={this.props.game_state}/>
                <DiceDisplay game_state={this.props.game_state}/>
                <EmojiChooser updateEmojiCallback={this.updateEmojiCallback}/>
                <UtilityMenu ws_manager={this.props.ws_manager}
                             match_state={this.props.match_state}
                />
            </div>
        )
    }
}

export default MainUtilityBar

