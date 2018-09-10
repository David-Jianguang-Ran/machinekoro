import React from "react"


import card_dex from "./cards"
import card_img from "./cardImg"
import ExpandableButton from "./expandableButton"

class Card extends ExpandableButton{
    /*
    This component is a card with a tap to expand detail view

    props:
    - name
    */
    constructor(props){
        super(props)
        this.button = (
            <div className={"main_card"}>
                <image src={card_img[this.props.name]} className={"main_card_image"}/>
            </div>
        )
        this.expanded = (
            <div>
                <p>{card_dex[this.props.name].toString()}</p>
            </div>
        )
    }
}

export default Card