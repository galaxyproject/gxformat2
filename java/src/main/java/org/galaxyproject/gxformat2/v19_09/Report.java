// Copyright Common Workflow Language project contributors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Saveable;

/**
 * Auto-generated interface for <I>https://galaxyproject.org/gxformat2/v19_09#Report</I><br>
 * This interface is implemented by {@link ReportImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * Definition of an invocation report for this workflow. Currently the only field is 'markdown'.
 *
 * </BLOCKQUOTE>
 */
public interface Report extends Saveable {
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#Report/markdown</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Galaxy flavored Markdown to define an invocation report. *
   *
   * </BLOCKQUOTE>
   */
  String getMarkdown();
}
