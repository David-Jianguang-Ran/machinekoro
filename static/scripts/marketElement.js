import React from "react"

import Card from "./card"

// the following component has props:
// title
// card_list
const MarketElement = (props) => (
    <div className={"sub_pop_up"}>
        <h6>{this.props.title}</h6>
        {this.peops.card_list.map((card,i) => (
            <Card name={card} key={i}/>
        ))}
    </div>
)
export default MarketElement