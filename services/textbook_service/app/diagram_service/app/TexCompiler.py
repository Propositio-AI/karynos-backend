import subprocess
import re
from pathlib import Path
from pdf2image import convert_from_path
import os
import uuid

from schema import (
    PointSchema,
    MinMaxSchema,
    FillStyle    
)
from shared.utils import readText
from pathlib import Path

from typing import List

TEX_SAVE_FOLDER = "./temp_tex/"
PDF_SAVE_FOLDER = "./temp_pdf/"
IMG_SAVE_FOLDER = "./temp_img/"

# Texヘッダー・フッターのパス
TEX_HEADER_PATH = "./tex_template/header.txt"
TEX_FOOTER_PATH = "./tex_template/footer.txt"

# 読み込み
TEX_HEADER = readText(TEX_HEADER_PATH)
TEX_FOOTER = readText(TEX_FOOTER_PATH)

class Compiler:           
    def add_deg(self, expr: str) -> str:
        """
        
        sin/cos/tanを度数法に変換する

        Parameters
        ----------
            expr: str
                元文字列
        
        Returns
        ----------
            str: 変換文字列

        Examples
        ----------
            expr = "sin(30) + cos(x) + tan(45)"
            return "sin(deg(30)) + cos(deg(x)) + tan(deg(45))"

        """

        trig_funcs = ['sin', 'cos', 'tan']

        def replacer(match):
            func = match.group(1)
            arg = match.group(2).strip()
            if arg.startswith('deg(') and arg.endswith(')'):
                return f"{func}({arg})"
            else:
                return f"{func}(deg({arg}))"

        pattern = re.compile(r'\b(' + '|'.join(trig_funcs) + r')\s*\(\s*([^\(\)]+?)\s*\)')
        new_expr = pattern.sub(replacer, expr)

        return new_expr

    def character_converter(self, char: str, value: float) -> str:
        """
        
        仮置き数値のTex変換

        Parameters
        ----------
            char: str
                仮置きする変数名
            value: float
                仮置きする値

        Returns
        ----------
            str: Tex
        
        """

        return "\n" + f"\\pgfmathsetmacro{{\\{char}}}{{{value}}}"
    
    def cal_converter(self, name, value):
        return "\n" + f"\\pgfmathsetmacro{{\\{name}}}{{{value}}}"
        
    # TODO: sizeを追加する
    def point_converter(self, label: str, x: float, y: float, size: float):
        """
        
        点のTex変換

        Parameters
        ----------
            label: str
                点のラベル
            x: float
                x座標
            y: float
                y座標
            size: float
                点の大きさ

        Returns
        ---------
            str: Tex

        """

        x = self.add_deg("{" + str(x) + "}")
        y = self.add_deg("{" + str(y) + "}")
        
        return f"""
            \\addplot[only marks, mark=*, mark size=2pt, color=red] coordinates {{({x},{y})}};
            \\node[blue, above right] at (axis cs:{x},{y}) {{${label}({x}, {y})$}};
        """

    def line_converter(self, width: int, start_x: float, start_y: float, end_x: float, end_y: float):
        """
        
        直線のTex変換

        Parameters
        ----------
            width: int
                線の幅
            start_x: float
                始点のx座標
            start_y: float
                始点のy座標
            end_x: float
                終点のx座標
            end_y: float
                終点のy座標

        Returns
        ----------
            str: Tex
                
       """

        start_x = self.add_deg("{" + str(start_x) + "}")
        start_y = self.add_deg("{" + str(start_y) + "}")
        end_x = self.add_deg("{" + str(end_x) + "}")
        end_y = self.add_deg("{" + str(end_y) + "}")

        return f"\\addplot[line width={width}pt, black] coordinates {{({start_x},{start_y}) ({end_x},{end_y})}};"


    def axis_converter(self, x_min: float, x_max: float, y_min: float, y_max: float) -> str:
        """
        
        座標軸のTex変換

        Parameters
        ----------
            x_min: float
                x軸最小値
            x_max: float
                x軸最大値
            y_min: float
                y軸最小値
            y_max: float
                y軸最大値

        Returns
        ----------
            str: Tex

        """

        return f"""
            width=15cm,
            height=15cm,
            axis equal image,
            axis lines=middle,
            grid=major,
            enlargelimits=false,
            clip=true,
            xlabel=$x$,
            ylabel=$y$,
            domain={x_min}:{x_max},
            ymin={y_min},ymax={y_max},
            view={{0}}{{90}},
            samples={200}
            ]
        """    

    def curve_explicit_converter(self, x_var: str, y_expr: str, width: int) -> str:
        """
        
        曲線(陽関数)のTex変換

        Parameters
        ----------
            x_var: str
                "x"のみ
            y_expr: str
                yの式
            width: int
                線の幅

        Returns
        ----------
            str: Tex

        
        """

        y_expr = self.add_deg(y_expr)

        return f"\\addplot[samples={200}, smooth, line width={width}pt, black, variable={x_var}] {{{y_expr}}};"

    def curve_implicit_converter(self, left: str, right: str) -> str:
        """
        
        曲線(陰関数)のTex変換

        Parameters
        ----------
            left: str
                曲線の方程式の左辺
            ritgh: str
                曲線の方程式の右辺

        Returns
        ----------
            str: Tex
        
        """

        return f"""
            \\addplot3 [
            contour gnuplot={{
                levels={{{right}}},
                labels=false
            }},
            ]
            {{{left}}};
        """

    def angle_converter(self, Ax: float, Ay: float, Bx: float, By: float, Cx: float, Cy: float, radius: float, long: float, theta: str):
        """
        
        角度のTex変換

        Parameters
        ----------
            Ax: float
                点Aのx座標
            Ay: float
                点Aのy座標
            Bx: float
                点Bのx座標
            By: float
                点Bのy座標
            Cx: float
                点Cのx座標
            Cy: float
                点Cのy座標
            radius: float
                半径
            long: float
                文字の中心からの距離
            theta: str
                角度

        Returns
        ----------
            str: Tex
        
        """

        return f"""
            \\coordinate (A) at ({Ax},{Ay});
            \\coordinate (B) at ({Bx},{By});
            \\coordinate (C) at ({Cx},{Cy});
            \\draw pic[draw=black, "${theta}$",angle eccentricity={long},angle radius={radius}cm] {{angle=C--B--A}};
        """

    def filldraw_converter(
        self,
        domain: MinMaxSchema,
        lower_expression: str,
        upper_expression: str,
        style: FillStyle,
        path_name_suffix: str
    ):
        """
        
        塗りつぶしのTex変換

        Parameters
        ----------
            domain: MinMaxSchema
                xの範囲
            lower_expression: str
                上限の式
            upper_expression: str
                下限の式
            style: FillStyle
                塗りつぶしのスタイル
            path_name_suffix: str

        Returns
        ----------
            str: Tex

        """

        return f"""
            \\addplot[
                name path=lowerBound{path_name_suffix},
                domain={domain.min}:{domain.max},
                samples={200},
                draw=none 
            ] {{{lower_expression}}};

            \\addplot[
                name path=upperBound{path_name_suffix},
                domain={domain.min}:{domain.max},
                samples={200},
                draw=none 
            ] {{{upper_expression}}};

            \\addplot[ 
                pattern=north east lines,
                pattern color=blue,
                draw= blue,
                line width={style.lineWidth}pt
            ] fill between[
                of=lowerBound{path_name_suffix} and upperBound{path_name_suffix},
                soft clip={{domain={domain.min}:{domain.max}}}
            ];

        """
    
    def convert(self, points: PointSchema) -> str:
        """
        
        図表設計をtexに変換する

        Parameters
        ----------
            points: PointSchema
                図表設計

        Returns
        ----------
            str: texの保存パス
        
        """

        macro_list = []
        axis_content_list = []

        # 座標軸
        for axis in points.axis:
            axis_content_list.append(
                self.axis_converter(
                    axis.x.min,
                    axis.x.max,
                    axis.y.min,
                    axis.y.max,
                )
            )

        # 曲線
        for curve in points.curves:
            if curve.functionType == "explicit":
                axis_content_list.append(
                    self.curve_explicit_converter(
                        curve.x.variable,
                        curve.y.expression,
                        curve.width
                    )
                )

            else:
                 axis_content_list.append(
                    self.curve_implicit_converter(
                        curve.expression.left,
                        curve.expression.right
                    )
                )

        # 変数
        for character in points.characterExpression:
            macro_list.append(
                self.character_converter(
                    character.char,
                    character.value
                )
            )

        # 点
        for point in points.points:
            axis_content_list.append(
                self.point_converter(
                    point.label,
                    point.position.x,
                    point.position.y,
                    point.size
                )
            )
        
        # 直線
        for line in points.lines:
            axis_content_list.append(
                self.line_converter(
                    line.width,
                    line.start.x,
                    line.start.y,
                    line.end.x,
                    line.end.y,
                )
            )

        # 角度
        for angle in points.angles:
            axis_content_list.append(
                self.angle_converter(
                    angle.coordinate[0].x, angle.coordinate[0].y, 
                    angle.coordinate[1].x, angle.coordinate[1].y, 
                    angle.coordinate[2].x, angle.coordinate[2].y, 
                    angle.radius,
                    angle.long,
                    angle.theta
                )
            )

        # 塗りつぶし
        for index, fill in enumerate(points.filldraw):
            axis_content_list.append(
                self.filldraw_converter(
                    fill.domain,
                    fill.lowerExpression,
                    fill.upperExpression,
                    fill.style,
                    index
                )
            )

        tex_code = "\n".join(macro_list) + "\n\\begin{axis}[" + "\n".join(axis_content_list) + "\n\\end{axis}"
        filepath = self.save_tex(tex_code)

        return filepath
       
    def save_tex(self, code: str) -> str:
        """
        
        Texコードの保存

        Parameters
        ----------
            code: str
                Texコード

        Returns
        ----------
            str: Texの保存場所
        
        """

        tex_path = f"{TEX_SAVE_FOLDER}{uuid.uuid4().hex}.tex"

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(TEX_HEADER)
            f.write(code)
            f.write("\n")
            f.write(TEX_FOOTER)

        return tex_path
    
    def tex_to_pdf(self, tex_path: str) -> str:
        """
        
        TexをPDFファイルに変換する

        Parameters
        ----------
            tex_path: str
                Texファイルのパス

        Returns
        ----------
            str: PDFファイルのパス
        
        """

        subprocess.run([
            "lualatex",
            "-shell-escape",
            "-interaction=nonstopmode",
            f"-output-directory={PDF_SAVE_FOLDER}",
            tex_path
        ], env={**os.environ, "LANG": "C"})

        basename = Path(tex_path).stem
        pdf_path = f"{PDF_SAVE_FOLDER}{basename}.pdf"

        self.remove_intermediate_file(basename)

        return pdf_path
    
    def remove_intermediate_file(self, basename: str):
        """
        
        TexからPDFの変換の際に作られる中間ファイルの削除

        Parameters
        ----------
            basename: str
                texのファイル名(拡張子なし)

        Returns
        ----------
            None
        
        """
        
        # 中間ファイルの拡張子リスト
        intermediate_extensions = [".aux", ".log", ".toc", ".out", ".lof", ".lot"]

        for ext in intermediate_extensions:
            file_to_remove = Path(f"{PDF_SAVE_FOLDER}{basename}{ext}")
            if file_to_remove.exists():
                file_to_remove.unlink() 

    def pdf_to_image(self, pdf_path: str) -> List[str]:
        """
        
        PDFファイルを画像に変換する関数

        Parameters
        ----------
            pdf_path: str
                PDFファイルのパス

        Returns
        ----------
            List[str]: 画像のパス
        
        """

        images = convert_from_path(pdf_path, output_folder = IMG_SAVE_FOLDER, fmt = 'png', output_file = Path(pdf_path).stem)
        
        cropped_paths = []
        # for img in images:
        #     left, upper, right, lower = 400, 200, 1250, 1300
        #     cropped = img.crop((left, upper, right, lower))

        #     original_path = Path(img.filename)  
        #     cropped_path = original_path  
        #     cropped.save(cropped_path)
        #     cropped_paths.append(str(cropped_path))

        return cropped_paths