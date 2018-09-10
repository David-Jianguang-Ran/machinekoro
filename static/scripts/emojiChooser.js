import { MdSentimentSatisfied } from "react-icons/md"
import React from "react"


import ExpandableButton from "./expandableButton"
import emojis from "./faces"

class EmojiChooser extends ExpandableButton{
    /*
    This component

    props:
    updateEmojiCallback

    */
    constructor(props){
        super(props)
        this.button = (
            <div className={"utility_button"}>
                <MdSentimentSatisfied/>
            </div>
        )
        this.expanded = (
            <div>
                {emojis.map(some_emoji => (
                    <div onClick={this.props.updateEmojiCallback(some.emoji.icon)}>
                        <span>{some_emoji.icon}</span>
                    </div>
                ))}
            </div>
        )
    }
}

export default EmojiChooser