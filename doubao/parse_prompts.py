#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包提示词解析脚本
解析2025豆包指令85+提示词合集中的Word和txt文件，提取标题、描述、内容和分类信息
"""

import os
import json
import re
from pathlib import Path
from docx import Document
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DouBaoPromptParser:
    def __init__(self, source_dir, output_file):
        self.source_dir = Path(source_dir)
        self.output_file = output_file
        self.prompts = []
        
        # 分类映射
        self.category_mapping = {
            '01自媒体类型': '自媒体',
            '02公文类': '公文写作',
            '03.英语类型': '英语学习',
            '04.论文类': '论文写作',
            '5.仿写类': '仿写创作',
            '6.影视小说类': '影视小说',
            '7.营销策划类': '营销策划',
            '8.职场类': '职场办公',
            '更新': '图像生成'
        }
    
    def extract_from_txt(self, file_path):
        """从txt文件中提取提示词信息"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 从文件名提取标题
            filename = file_path.stem
            title = filename.replace('.txt', '')
            
            # 尝试从内容中提取更好的标题和描述
            lines = content.split('\n')
            description = ""
            
            # 查找Role或标题行
            for i, line in enumerate(lines[:10]):  # 只检查前10行
                line = line.strip()
                if line.startswith('## Role') and i + 1 < len(lines):
                    potential_title = lines[i + 1].strip()
                    if potential_title and len(potential_title) < 50:
                        title = potential_title
                elif line.startswith('## Background') and i + 1 < len(lines):
                    potential_desc = lines[i + 1].strip()
                    if potential_desc and len(potential_desc) < 200:
                        description = potential_desc
            
            # 如果没有找到描述，使用内容的前100个字符
            if not description:
                clean_content = re.sub(r'##.*?\n', '', content)
                clean_content = re.sub(r'\n+', ' ', clean_content).strip()
                description = clean_content[:100] + "..." if len(clean_content) > 100 else clean_content
            
            return {
                'title': title,
                'description': description,
                'content': content
            }
            
        except Exception as e:
            logger.error(f"解析txt文件失败 {file_path}: {e}")
            return None
    
    def extract_from_docx(self, file_path):
        """从docx文件中提取提示词信息"""
        try:
            doc = Document(file_path)
            
            # 提取所有段落文本
            paragraphs = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            
            if not paragraphs:
                return None
            
            # 从文件名提取标题
            filename = file_path.stem
            title = filename.replace('.docx', '')
            
            # 合并所有段落作为内容
            content = '\n'.join(paragraphs)
            
            # 提取描述（使用前几个段落或第一个较长的段落）
            description = ""
            for para in paragraphs[:3]:
                if len(para) > 20 and len(para) < 200:
                    description = para
                    break
            
            if not description and paragraphs:
                # 使用第一个段落的前100个字符
                first_para = paragraphs[0]
                description = first_para[:100] + "..." if len(first_para) > 100 else first_para
            
            return {
                'title': title,
                'description': description,
                'content': content
            }
            
        except Exception as e:
            logger.error(f"解析docx文件失败 {file_path}: {e}")
            return None
    
    def get_category_from_path(self, file_path):
        """从文件路径获取分类"""
        path_parts = file_path.parts
        
        # 查找分类目录
        for part in path_parts:
            if part in self.category_mapping:
                return self.category_mapping[part]
        
        # 默认分类
        return "其他"
    
    def clean_title(self, title):
        """清理标题，移除不必要的字符"""
        # 移除常见的前缀数字和符号
        title = re.sub(r'^\d+[、.]?\s*', '', title)
        title = re.sub(r'【.*?】', '', title)  # 移除【指令+教程】等标记
        title = title.strip()
        return title if title else "未命名提示词"
    
    def parse_all_files(self):
        """解析所有文件"""
        logger.info(f"开始解析目录: {self.source_dir}")
        
        # 遍历所有文件
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                
                # 跳过不需要的文件
                if suffix in ['.mp4', '.jpg', '.png', '.pdf', '.bat']:
                    continue
                
                logger.info(f"处理文件: {file_path}")
                
                # 解析文件
                data = None
                if suffix == '.txt':
                    data = self.extract_from_txt(file_path)
                elif suffix == '.docx':
                    data = self.extract_from_docx(file_path)
                
                if data:
                    # 获取分类
                    category = self.get_category_from_path(file_path)
                    
                    # 清理标题
                    title = self.clean_title(data['title'])
                    
                    # 构建提示词对象
                    prompt = {
                        "提示词名称": title,
                        "提示词描述": data['description'],
                        "提示词内容": data['content'],
                        "提示词分类": category
                    }
                    
                    self.prompts.append(prompt)
                    logger.info(f"成功解析: {title} (分类: {category})")
        
        logger.info(f"总共解析了 {len(self.prompts)} 个提示词")
    
    def save_to_json(self):
        """保存为JSON格式"""
        output_data = {
            "prompts": self.prompts
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {self.output_file}")
    
    def run(self):
        """运行解析流程"""
        self.parse_all_files()
        self.save_to_json()
        
        # 打印统计信息
        categories = {}
        for prompt in self.prompts:
            cat = prompt['提示词分类']
            categories[cat] = categories.get(cat, 0) + 1
        
        logger.info("分类统计:")
        for cat, count in categories.items():
            logger.info(f"  {cat}: {count} 个")

if __name__ == "__main__":
    # 配置路径
    source_directory = r"f:\个人文档\website\salary\2025豆包指令85+提示词合集"
    output_file = r"f:\个人文档\website\salary\doubao\prompts.json"
    
    # 创建解析器并运行
    parser = DouBaoPromptParser(source_directory, output_file)
    parser.run()