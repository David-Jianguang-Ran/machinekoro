import {MdStore} from "react-icons/md"
import React from "react"


import ExpandableButton from "./expandableButton"
import MarketElement from "./marketElement"

class MarketDisplay extends ExpandableButton{
    /*
    props:
        - game_state

     */
    constructor(props){
        super(props)
        this.button = (
            <div>
                <MdStore className={"utility_button"}/>
            </div>
        )
        this.expanded = (
            <div>
                <MarketElement title={"Activation < 7"}
                               card_list={this.props.game_state.market.low}/>
                <MarketElement title={"Activation > 6"}
                               card_list={this.props.game_state.market.high}/>
                <MarketElement title={"Major Establishment Cards"}
                               card_list={this.props.game_state.market.purple}/>
            </div>
        )
    }
}

export default MarketDisplay