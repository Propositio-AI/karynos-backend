from pydantic import BaseModel, Field
from typing import List, Literal

class OutlineSchema(BaseModel):
    points: List[str] = Field(..., description="点の座標、色、サイズについての図表")
    lines: List[str] = Field(..., description="線の始点の座標、終点の座標、サイズについての図表")
    axis: List[str] = Field(..., description="座標軸のxの範囲、yの範囲、サンプル数についての図表")
    curves: List[str] = Field(..., description="曲線のxの範囲、yの範囲、サンプル数、サイズ、関数の種類(陰関数、陽関数)についての図表　(円もcurvesに入ります。また、曲線以外は考えないこと。曲線とは2次関数、３次関数、三角関数、円などのことを指します。直線は'curves'には含まれません。'直線は一次関数の特殊な場合なので、曲線として表現'のような考え方はしないこと。)")
    characterExpression: List[str] = Field(..., description="変数について数値を決める(例：'m'に'1'を定義する)※任意の数値ではなく、int型の数値を定義してください。")
    angles: List[str] = Field(..., description="角度の始点の座標、終点の座標、スタートの角度、終わりの角度、半径についての図表")
    filldraws: List[str] = Field(..., description="塗りつぶしのxの範囲、どのようなところに塗りつぶしをするのか、塗り色、サンプル数、サイズについての図表")
    
    class Config:
        description = "図表概要"
        extra = "forbid" 

class XYSchema(BaseModel):
    label: str = Field(..., description="点ラベル")
    x: float = Field(..., description="x座標")
    y: float = Field(..., description="y座標")

    class Config:
        description = "x-y軸の表現"
        extra = "forbid" 

class MinMaxSchema(BaseModel):
    min: float = Field(..., description="最低値")
    max: float = Field(..., description="最大値")

    class Config:
        description = "範囲"
        extra = "forbid" 

class LeftRightSchema(BaseModel):
    left: str = Field(..., description="左辺の式(変数xやyを含む)")
    right: str = Field(..., description="右辺の定数(数値のみ)")

    class Config:
        description = "方程式"
        extra = "forbid" 

class FillStyle(BaseModel):
    fill: str = Field(..., description="塗りつぶし色")
    draw: str = Field(..., description="境界線色")
    lineWidth: str = Field(..., description="線幅")

    class Config:
        description = "塗りつぶしスタイル"
        extra = "forbid" 

class FigPointSchema(BaseModel):
    label: str = Field(..., description="点の名前(例：'A', 'B)")
    role: str = Field(..., description="点の役割の説明(例：'頂点', '交点') – 変数や動かせる点は含めない")
    position: XYSchema
    size: float = Field(..., description="点の表示サイズ")

    class Config:
        description = "点"
        extra = "forbid" 

class FigLineSchema(BaseModel):
    start: XYSchema
    end: XYSchema
    width: int = Field(..., description="線の太さ")

    class Config:
        description = "直線"
        extra = "forbid" 

class FigAxisSchema(BaseModel):
    x: MinMaxSchema
    y: MinMaxSchema

    class Config:
        description = "座標軸"
        extra = "forbid" 

class CurveXSchema(BaseModel):
    variable: str = Field(..., description="xのみ")
    range: MinMaxSchema

    class Config:
        description = "曲線の式xについて"
        extra = "forbid" 

class CurveYSchema(BaseModel):
    expression: str = Field(..., description="yの式(TikZ記法、例：`sqrt(x)`)")
    range: MinMaxSchema

    class Config:
        description = "曲線の式のyについて"
        extra = "forbid" 

class FigCurveSchema(BaseModel):
    allExpression: str = Field(..., description="x軸の範囲")
    functionType: Literal["explicit", "implicit"] = Field(..., description="explicit: 陽関数・implicit: 陰関数")
    expression: LeftRightSchema
    x: CurveXSchema
    y: CurveYSchema
    width: int = Field(..., description="線の太さ")
    height: int = Field(..., description="高さ")

    class Config:
        description = "曲線"
        extra = "forbid" 

class FigAngleSchema(BaseModel):
    coordinate: List[XYSchema] = Field(..., description="3点の間の座標('A':(0,0), 'B'(2,2), 'C'(3,-1))", min_length=3, max_length=3)
    radius: float = Field(..., description="半径")
    long: float = Field(..., description="文字列を配置する場所(中心からの離れ具合)")
    aim: List[Literal[0, 1, 2]] = Field(..., description="3点のどこの角度を示すか(間にある点が角度を表示される)coordinateの配列に対応",  min_length=3, max_length=3)
    theta: str = Field(..., description="角度の数値を表示(数値なら'30'などを入れ、thetaを入れる場合は、'\\theta'を代入してください。)")

    class Config:
        description = "角度の表示"
        extra = "forbid"        

class FigFillSchema(BaseModel):
    domain: MinMaxSchema
    lowerExpression: str = Field(..., description="下限式(TikZ記法)")
    upperExpression: str = Field(..., description="上限式(TikZ記法)")
    style: FillStyle

    class Config:
        description = "塗りつぶし"
        extra = "forbid" 

class FigCharSchema(BaseModel):
    char: str = Field(..., description="数字を仮置きする変数名")
    value: float = Field(..., description="数値")
    
    class Config:
        description = "変数の仮値"
        extra = "forbid" 

class FigCalcSchema(BaseModel):
    expression: str = Field(..., description="LaTeX互換の式(例：`'sqrt(2)'`、`'tan(deg(30))'`)")

    class Config:
        description = "計算式"
        extra = "forbid" 

class PointSchema(BaseModel):
    points: List[FigPointSchema] = Field(..., description="pointsは図中の点の要素に関する設計の詳細を定めます。")
    lines: List[FigLineSchema] = Field(..., description="linesは図中の線に関する詳細の設計を定めます。")
    axis: List[FigAxisSchema] = Field(..., description="axisは図中の軸に関する設計の詳細を定めます")
    curves: List[FigCurveSchema] = Field(..., description="curvesは曲線のみを扱います。直線についてはlinesを使用して設計してください")
    characterExpression: List[FigCharSchema] = Field(..., description="characterExpressionは設計図中で使用されている変数に仮の値を代入して図表を描画するための要素です。")
    caluculates: List[FigCalcSchema] = Field(..., description="複雑な式を表すためのもので、`coordinate`で直接使えない場合に使用します。")
    angles: List[FigAngleSchema] = Field(..., description="図中で角度に関して描画したい際に使用する要素です。")
    filldraw: List[FigFillSchema] = Field(..., description="図中において曲線間の塗りつぶし領域を定義します")

    class Config:
        description = "図表設計"
        extra = "forbid" 