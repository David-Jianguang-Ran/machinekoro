import React from "react"

class EmoFace extends React.Component{
    /*
    This component
    */
    constructor(props){
        super(props)
        this.faces = {
            "tiger": "/static/assets/faces/tiger.jpeg",
            "wolf": "/static/assets/faces/wolf.jpeg",
            "sloth": "/static/assets/faces/sloth.jpeg",
            "owl": "/static/assets/faces/owl.jpeg",
            "horse": "/static/assets/faces/horse.jpeg",
            "flower":"/static/assets/faces/flower.jpeg",
            "404" : "/static/assets/faces/404.jpeg"
        }
        this.emojis = {
            "smile": "😃",
            "sweat": "😓",
            "tongue":"😋",
            "shades":"😎",
            "angry":"😡",
            "money":"🤑",
        }
    }
    render(){
        return(
            <div>
                <emoji selected_emoji={this.emojis[this.props.player.emoji]}/>
            </div>
        )
    }
}

const emoji = (props) => (
    <span role={img}>{this.props.selected_emoji}</span>
)