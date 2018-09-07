import React from "react"


// this is simply a span object that wraps around a emoji
const Emoji = (props) => (
    <span role={img}>{this.props.selected_emoji}</span>
)

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
            "sad":"😥",
            "zzz":"😴",
            "bot":"🤖",
            "404":"💩"
        }
    }
    render(){
        return(
            <div className={"emo_face"}>
                <img src={this.faces[this.props.player.face]} className={"emo_face_lg"}/>
                <Emoji classname={"emo_face_sm"} selected_emoji={this.emojis[this.props.player.emoji]}/>
            </div>
        )
    }
}

EmoFace.defaultProps = {
    player:{
        face:"404",
        emoji:"404"
    }
}

export default EmoFace

