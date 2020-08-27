import logging
import re

from extractors import Block
from extractors import Extractor
from extractors import ExtractionResult


class RegexExtractor(Extractor):
    def __init__(self, default_output, begin_block_regex, end_block_regex, skip_block_regex, filename_block_regex):
        super().__init__(default_output)
        self.__logger = logging.getLogger('RegexExtractor')
        self.begin_block_regex = begin_block_regex
        self.end_block_regex = end_block_regex
        self.skip_block_regex = skip_block_regex
        self.filename_block_regex = filename_block_regex

    def extract_blocks(self, file):
        extracted_blocks = []
        total_code_blocks = 0
        total_skipped_blocks = 0

        block_data = []
        block_started = False
        current_filename = self.default_output
        block_id = 0
        skip = False
        begin_line = 0

        for line_number, line in enumerate(file):

            if re.match(self.begin_block_regex, line):
                block_started = True
                block_id += 1
                total_code_blocks += 1
                begin_line = line_number + 1
                self.__logger.debug("Found block #{} starter at line number {}".format(block_id, line_number))
                if re.match(self.skip_block_regex, line) is not None:
                    self.__logger.debug("\tBlock #{} will be skipped".format(block_id))
                    skip = True
                    total_skipped_blocks += 1
                    continue
                m = re.match(self.filename_block_regex, line)
                if m is not None:
                    current_filename = m.group(1)
                self.__logger.debug("\tBlock #{} will be extracted to {}".format(block_id, current_filename))
                continue

            if re.match(self.end_block_regex, line):
                self.__logger.debug("\tFound block #{} end at line number {}".format(block_id, line_number))
                self.__logger.debug("\tTotal lines in block #{}: {}".format(block_id, len(block_data)))
                block_started = False
                extracted_blocks.append(Block(block_id, begin_line, line_number - 1, skip, current_filename, "".join(block_data)))
                current_filename = self.default_output
                block_data = []
                skip = False

            if block_started:
                block_data.append(line)
                continue

        return ExtractionResult(extracted_blocks, total_code_blocks, total_skipped_blocks)
