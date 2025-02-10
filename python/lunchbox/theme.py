from typing import Type  # noqa: F401

from enum import Enum
# ------------------------------------------------------------------------------


class Colorscheme(Enum):
    '''
    Henanigans color scheme.
    '''
    DARK1 = '#040404'
    DARK2 = '#181818'
    BG = '#242424'
    GREY1 = '#343434'
    GREY2 = '#444444'
    LIGHT1 = '#A4A4A4'
    LIGHT2 = '#F4F4F4'
    DIALOG1 = '#444459'
    DIALOG2 = '#5D5D7A'
    RED1 = '#F77E70'
    RED2 = '#DE958E'
    ORANGE1 = '#EB9E58'
    ORANGE2 = '#EBB483'
    YELLOW1 = '#E8EA7E'
    YELLOW2 = '#E9EABE'
    GREEN1 = '#8BD155'
    GREEN2 = '#A0D17B'
    CYAN1 = '#7EC4CF'
    CYAN2 = '#B6ECF3'
    BLUE1 = '#5F95DE'
    BLUE2 = '#93B6E6'
    PURPLE1 = '#C98FDE'
    PURPLE2 = '#AC92DE'


def get_plotly_template(colorscheme=Colorscheme):
    # type: (Type[Colorscheme]) -> dict
    '''
    Create a plotly template from a given color scheme.

    Args:
        colorscheme (colorscheme): colorscheme enum.

    Returns:
        dict: Plotly template.
    '''
    cs = colorscheme
    colors = [
        cs.CYAN2, cs.RED2, cs.GREEN2, cs.BLUE2, cs.ORANGE2, cs.PURPLE2,
        cs.YELLOW2, cs.LIGHT2, cs.DARK2, cs.GREY2, cs.CYAN1, cs.RED1, cs.GREEN1,
        cs.BLUE1, cs.ORANGE1, cs.PURPLE1, cs.YELLOW1, cs.LIGHT1, cs.DARK1,
        cs.GREY1,
    ]

    template = dict(
        layout=dict(
            colorway=[x.value for x in colors],
            plot_bgcolor=cs.DARK2.value,
            paper_bgcolor=cs.DARK2.value,
            bargap=0.15,
            bargroupgap=0.05,
            autosize=True,
            margin=dict(t=80, b=65, l=80, r=105),
            title=dict(font=dict(
                color=cs.LIGHT2.value,
                size=30,
            )),
            legend=dict(
                font=dict(color=cs.LIGHT2.value),
                bgcolor=cs.BG.value,
                bordercolor=cs.BG.value,
                indentation=5,
                borderwidth=4,
            ),
            xaxis=dict(
                title=dict(font=dict(
                    color=cs.LIGHT2.value,
                    size=16,
                )),
                gridcolor=cs.BG.value,
                zerolinecolor=cs.GREY1.value,
                zerolinewidth=5,
                tickfont=dict(color=cs.LIGHT1.value),
                showgrid=True,
                autorange=True,
            ),
            yaxis=dict(
                title=dict(font=dict(
                    color=cs.LIGHT2.value,
                    size=16,
                )),
                gridcolor=cs.BG.value,
                zerolinecolor=cs.GREY1.value,
                zerolinewidth=5,
                tickfont=dict(color=cs.LIGHT1.value),
                showgrid=True,
                autorange=True,
            )
        )
    )
    return template
